import addonHandler
import globalPluginHandler
import scriptHandler
import ui
import gui
import wx
import webbrowser
import os
import shutil
import psutil
from datetime import datetime
import logging

addonHandler.initTranslation()

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='browser_history_remover.log')

class BrowserHistoryRemoverDialog(wx.Dialog):
    title = _("Browser History Remover")

    def __init__(self, parent):
        try:
            super().__init__(parent, title=self.title)
            self.initUI()
            self.Centre()
        except Exception as e:
            logging.error(f"Error initializing BrowserHistoryRemoverDialog: {str(e)}")
            gui.messageBox(
                _("Failed to initialize the dialog: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )
            self.Destroy()

    def initUI(self):
        try:
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=mainSizer)

            # Browser selection dropdown
            self.browserChoices = [_("Google Chrome"), _("Microsoft Edge"), _("Firefox"), _("Internet Explorer")]
            browserLabel = _("Select a browser:")
            self.browserCombo = sHelper.addLabeledControl(browserLabel, wx.Choice, choices=self.browserChoices)
            self.browserCombo.SetSelection(0)  # Default to Google Chrome

            # Delete history button
            self.deleteButton = sHelper.addItem(wx.Button(self, label=_("Delete browsing history")))
            self.deleteButton.Bind(wx.EVT_BUTTON, self.onDeleteHistory)

            # Backup option
            self.backupCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("Create backup before deletion")))
            self.backupCheckbox.SetValue(False)

            # About button
            self.aboutButton = sHelper.addItem(wx.Button(self, label=_("About")))
            self.aboutButton.Bind(wx.EVT_BUTTON, self.onAbout)

            # Exit button
            self.exitButton = sHelper.addItem(wx.Button(self, label=_("Exit")))
            self.exitButton.Bind(wx.EVT_BUTTON, self.onExit)

            self.SetSizerAndFit(mainSizer)
            self.browserCombo.SetFocus()
        except Exception as e:
            logging.error(f"Error setting up UI: {str(e)}")
            gui.messageBox(
                _("Failed to set up the dialog interface: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )
            self.Destroy()

    def onDeleteHistory(self, evt):
        try:
            selected_browser = self.browserChoices[self.browserCombo.GetSelection()]
            
            if not self.isBrowserInstalled(selected_browser):
                gui.messageBox(
                    _("Sorry, {browser} is not installed on your computer. Please select another browser.").format(browser=selected_browser),
                    _("Error"),
                    wx.OK | wx.ICON_ERROR
                )
                return

            confirm = gui.messageBox(
                _("Are you sure you want to remove browsing history for {browser}?").format(browser=selected_browser),
                _("Warning"),
                wx.YES_NO | wx.ICON_WARNING
            )
            if confirm == wx.ID_NO:
                self.Destroy()
                return

            # Close browser before deletion
            self.closeBrowser(selected_browser)

            # Create backup if selected
            if self.backupCheckbox.GetValue():
                self.createBackup(selected_browser)

            # Perform deletion
            self.deleteBrowserHistory(selected_browser)
            gui.messageBox(
                _("Browsing history for {browser} has been deleted successfully.").format(browser=selected_browser),
                _("Success"),
                wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            logging.error(f"Error during history deletion for {selected_browser}: {str(e)}")
            gui.messageBox(
                _("Error deleting browsing history for {browser}: {error}").format(
                    browser=selected_browser, error=str(e)
                ),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )

    def isBrowserInstalled(self, browser):
        try:
            user_profile = os.path.expanduser("~")
            paths = {
                _("Google Chrome"): os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data", "Default"),
                _("Microsoft Edge"): os.path.join(user_profile, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default"),
                _("Firefox"): os.path.join(user_profile, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles"),
                _("Internet Explorer"): os.path.join(user_profile, "AppData", "Local", "Microsoft", "Windows", "History")
            }
            browser_path = paths.get(browser, "")
            if not browser_path:
                raise ValueError(f"Unknown browser: {browser}")
            return os.path.exists(browser_path)
        except Exception as e:
            logging.error(f"Error checking if {browser} is installed: {str(e)}")
            return False

    def closeBrowser(self, browser):
        try:
            browser_processes = {
                _("Google Chrome"): "chrome.exe",
                _("Microsoft Edge"): "msedge.exe",
                _("Firefox"): "firefox.exe",
                _("Internet Explorer"): "iexplore.exe"
            }
            
            process_name = browser_processes.get(browser)
            if not process_name:
                raise ValueError(f"No process name defined for {browser}")
            
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    except psutil.Error as e:
                        logging.error(f"Error terminating process {process_name}: {str(e)}")
        except Exception as e:
            logging.error(f"Error closing {browser}: {str(e)}")
            raise Exception(f"Failed to close {browser}: {str(e)}")

    def createBackup(self, browser):
        try:
            user_profile = os.path.expanduser("~")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(user_profile, "BrowserHistoryBackups", browser, timestamp)
            os.makedirs(backup_dir, exist_ok=True)

            if browser in [_("Google Chrome"), _("Microsoft Edge")]:
                source_path = os.path.join(user_profile, "AppData", "Local", 
                    "Google" if browser == _("Google Chrome") else "Microsoft", 
                    "Chrome" if browser == _("Google Chrome") else "Edge", 
                    "User Data", "Default")
                history_files = ["History", "History-journal"]
                for file in history_files:
                    file_path = os.path.join(source_path, file)
                    if os.path.exists(file_path):
                        shutil.copy(file_path, backup_dir)
        
            elif browser == _("Firefox"):
                source_path = os.path.join(user_profile, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
                if os.path.exists(source_path):
                    for profile in os.listdir(source_path):
                        profile_path = os.path.join(source_path, profile)
                        if os.path.isdir(profile_path):
                            shutil.copytree(profile_path, os.path.join(backup_dir, profile), dirs_exist_ok=True)
        
            elif browser == _("Internet Explorer"):
                source_path = os.path.join(user_profile, "AppData", "Local", "Microsoft", "Windows", "History")
                if os.path.exists(source_path):
                    shutil.copytree(source_path, backup_dir, dirs_exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating backup for {browser}: {str(e)}")
            raise Exception(f"Failed to create backup for {browser}: {str(e)}")

    def deleteBrowserHistory(self, browser):
        try:
            user_profile = os.path.expanduser("~")
            
            if browser in [_("Google Chrome"), _("Microsoft Edge")]:
                base_path = os.path.join(user_profile, "AppData", "Local", 
                    "Google" if browser == _("Google Chrome") else "Microsoft", 
                    "Chrome" if browser == _("Google Chrome") else "Edge", 
                    "User Data", "Default")
                history_files = ["History", "History-journal"]
                for file in history_files:
                    file_path = os.path.join(base_path, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            elif browser == _("Firefox"):
                firefox_path = os.path.join(user_profile, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
                if os.path.exists(firefox_path):
                    for profile in os.listdir(firefox_path):
                        history_db = os.path.join(firefox_path, profile, "places.sqlite")
                        if os.path.exists(history_db):
                            os.remove(history_db)
            
            elif browser == _("Internet Explorer"):
                history_path = os.path.join(user_profile, "AppData", "Local", "Microsoft", "Windows", "History")
                if os.path.exists(history_path):
                    shutil.rmtree(history_path, ignore_errors=True)
        except Exception as e:
            logging.error(f"Error deleting history for {browser}: {str(e)}")
            raise Exception(f"Failed to delete history for {browser}: {str(e)}")

    def onAbout(self, evt):
        try:
            aboutDialog = AboutDialog(self)
            aboutDialog.ShowModal()
            aboutDialog.Destroy()
        except Exception as e:
            logging.error(f"Error opening About dialog: {str(e)}")
            gui.messageBox(
                _("Failed to open About dialog: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )

    def onExit(self, evt):
        try:
            self.Destroy()
        except Exception as e:
            logging.error(f"Error closing dialog: {str(e)}")

class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        try:
            super().__init__(parent, title=_("About the Developer"))
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            message = wx.StaticText(self, label=_("Hi, I am Sujan Rai from Tech Visionary Nepal. Do you want to join my official Telegram channel and get daily life useful and unique resources?"))
            sizer.Add(message, 0, wx.ALL, 10)
            
            buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            joinButton = wx.Button(self, label=_("Join"))
            joinButton.Bind(wx.EVT_BUTTON, self.onJoin)
            buttonSizer.Add(joinButton, 0, wx.RIGHT, 5)
            
            noThanksButton = wx.Button(self, label=_("No Thanks"))
            noThanksButton.Bind(wx.EVT_BUTTON, self.onNoThanks)
            buttonSizer.Add(noThanksButton, 0, wx.LEFT, 5)
            
            sizer.Add(buttonSizer, 0, wx.CENTER | wx.ALL, 10)
            
            self.SetSizerAndFit(sizer)
            self.Centre()
        except Exception as e:
            logging.error(f"Error initializing AboutDialog: {str(e)}")
            gui.messageBox(
                _("Failed to initialize About dialog: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )
            self.Destroy()

    def onJoin(self, event):
        try:
            webbrowser.open("https://t.me/techvisionary")
            self.Destroy()
        except Exception as e:
            logging.error(f"Error opening Telegram link: {str(e)}")
            gui.messageBox(
                _("Failed to open Telegram link: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )

    def onNoThanks(self, event):
        try:
            self.Destroy()
        except Exception as e:
            logging.error(f"Error closing About dialog: {str(e)}")

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        try:
            super().__init__()
            self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
            self.browserHistoryRemoverItem = self.toolsMenu.Append(wx.ID_ANY, _("Browser History Remover"), _("Open the browser history remover"))
            gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onBrowserHistoryRemover, self.browserHistoryRemoverItem)
        except Exception as e:
            logging.error(f"Error initializing GlobalPlugin: {str(e)}")
            gui.messageBox(
                _("Failed to initialize plugin: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )

    def terminate(self):
        try:
            self.toolsMenu.Remove(self.browserHistoryRemoverItem)
        except Exception as e:
            logging.error(f"Error terminating plugin: {str(e)}")

    def onBrowserHistoryRemover(self, evt):
        wx.CallAfter(self.showDialog)

    def showDialog(self):
        dialog = BrowserHistoryRemoverDialog(gui.mainFrame)
        dialog.ShowModal()
        dialog.Destroy()

    @scriptHandler.script(
        description=_("Opens the browser history remover"),
        category=_("Browser history remover"),
        gesture="kb:NVDA+alt+b"
    )
    def script_openBrowserHistoryRemover(self, gesture):
        try:
            wx.CallAfter(self.showDialog)
        except Exception as e:
            logging.error(f"Error executing script: {str(e)}")
            gui.messageBox(
                _("Failed to execute script: {error}").format(error=str(e)),
                _("Error"),
                wx.OK | wx.ICON_ERROR
            )