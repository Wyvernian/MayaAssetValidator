import importlib
import MayaAssetValidator.scripts.mainWindow as mainWindow

importlib.reload(mainWindow)
mainWindow.show_window()