import c4d

def CreateSplitterMenu():
    mainMenu = c4d.gui.GetMenuResource("M_EDITOR")
    pluginsMenu = c4d.gui.SearchPluginMenuResource()

    menu = c4d.BaseContainer()
    menu.InsData(c4d.MENURESOURCE_SUBTITLE, "Google")
    menu.InsData(c4d.MENURESOURCE_COMMAND, str("PLUGIN_CMD_" + str(1062995))) # splitter

    if pluginsMenu:
        # Insert menu after 'Plugins' menu
        mainMenu.InsDataAfter(c4d.MENURESOURCE_STRING, menu, pluginsMenu)
    else:
        # Insert menu after the last existing menu ('Plugins' menu was not found)
        mainMenu.InsData(c4d.MENURESOURCE_STRING, menu)

def PluginMessage(id, data):
    if id == c4d.C4DPL_BUILDMENU:
        CreateSplitterMenu()