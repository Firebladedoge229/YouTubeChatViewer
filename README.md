![YouTube Chat Viewer](https://github.com/Firebladedoge229/YouTubeChatViewer/blob/main/youtubechatviewer.png?raw=true)

# YouTube Chat Viewer

Lightweight application for viewing YouTube chat in a livestream.

![Showcase](https://i.ibb.co/3FNZThy/You-Tube-Chat-Viewer-b1.png)

## Installation

Simply run the executable found at the [Releases](https://github.com/Firebladedoge229/YouTubeChatViewer/releases/latest) page.

A [Windows Defender SmartScreen](https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/) window may display, or your anti-virus might trigger, this is due to the application signing system by [PyInstaller](https://github.com/pyinstaller/pyinstaller).

If you are suspicious, feel free to compile the code yourself!

### Build Command
```py
pyinstaller --onefile --noconsole --icon=icon.ico --add-data="icon.ico;." --add-data="sv_ttk;sv_ttk" youtubechatviewer.py
```

## Author

[Firebladedoge229](https://www.github.com/Firebladedoge229) - Creator

## Credits 

[IconArchive](https://www.iconarchive.com/show/classic-3d-social-icons-by-graphics-vibe/youtube-icon.html) - YouTube Icon
