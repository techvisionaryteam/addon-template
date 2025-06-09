# Browser History Remover (NVDA Addon)

## 📌 Overview

**Browser History Remover** is an NVDA (NonVisual Desktop Access) addon that allows screen reader users to **securely and easily delete their browser history** from major web browsers directly through NVDA's interface. It provides a clean and accessible graphical user interface for selecting the browser and deleting its history files.

This addon supports **Google Chrome**, **Microsoft Edge**, **Mozilla Firefox**, and **Internet Explorer**, making it a powerful utility for privacy-conscious users and those who need to manage browsing traces efficiently.

---

## 🎯 Features

- ✅ **Graphical Interface**: Easy-to-use settings dialog accessible via NVDA Tools menu or keyboard shortcut.
- ✅ **Supports Multiple Browsers**: Chrome, Edge, Firefox, and Internet Explorer.
- ✅ **Single-click Deletion**: Delete browser history with one button press.
- ✅ **Safe Deletion**: Attempts graceful file deletion and handles exceptions.
- ✅ **About Dialog**: Offers a link to join a Telegram channel for useful resources.
- ✅ **Keyboard Shortcut Support**: Launch the tool via `NVDA+Alt+B`.

---

## 🖥️ User Interface

### Main Dialog

- **Dropdown** to select the browser.
- **Button**: “Delete all history items” – deletes history files for the selected browser.
- **Button**: “About” – opens a dialog promoting a Telegram channel.

### About Dialog

- Displays a message with a call to action.
- Buttons:
  - `Join`: Opens the Telegram channel in the default browser.
  - `No thanks`: Closes the dialog.

---

## 🔐 How It Works

This addon accesses and deletes history files from standard locations in the Windows file system. Here's how it deletes data:

| Browser | Targeted Files |
|---------|----------------|
| Google Chrome | `History`, `History-journal` |
| Microsoft Edge | `History`, `History-journal` |
| Firefox | `places.sqlite` in all Firefox profiles |
| Internet Explorer | Deletes entire `History` folder |

> Note: The addon works based on default file paths and assumes standard installations. For portable or non-default paths, deletion might not occur.

---

## 🧠 Keyboard Shortcut

| Gesture | Action |
|---------|--------|
| `NVDA + Alt + B` | Opens the Browser History Remover dialog |

You can customize or view this shortcut from NVDA's input gesture manager.

---

## 📂 Installation

1. Download the addon (`.nvda-addon` file).
2. In NVDA, open the **Tools** menu → **Manage Add-ons**.
3. Choose **Install** and browse to the addon file.
4. Restart NVDA when prompted.

Once installed, access the tool via:

- `NVDA menu → Tools → Browser History Remover`
- Or use the hotkey `NVDA + Alt + B`

---

## 📜 Code Structure

- `BrowserHistoryRemoverDialog`: Main dialog for browser selection and history deletion.
- `deleteBrowserHistory`: Handles the logic of deleting browser-specific history.
- `AboutDialog`: Popup that promotes a Telegram resource channel.
- `GlobalPlugin`: Registers the addon in NVDA and adds menu item and shortcut.

---

## 🔗 Telegram Channel

Want to receive useful daily tips and resources?

Join our [Telegram Channel](https://t.me/techvisionary) 💡

---

## ⚠️ Disclaimer

- This tool deletes local history files and does **not** remove synced or cloud-based data.
- Use responsibly. Deleted files **cannot be recovered**.
- Internet Explorer is deprecated on newer Windows versions — behavior may vary.

---

## 🛠️ Developers

This addon was built with accessibility and privacy in mind, using NVDA's GUI and plugin APIs. You're welcome to contribute or fork the project!

Feel free to open issues or improvements.

---

## 📃 License

This addon is provided under the **GNU-GPL v2 License**.

---

**Created with ❤️ for the NVDA community by [TechVisionary](https://t.me/techvisionary)**

