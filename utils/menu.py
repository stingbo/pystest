# coding = utf-8


class Menu:
    def getMenu(config, key):
        data = []
        menus = config.get('MENU')
        keys = key.split('.')

        return Menu.getMenuPath(menus, keys, data)

    def getMenuPath(menus, keys, data=[], parent_key=''):
        for menu in menus:
            if menu.get('key') in keys:
                if parent_key:
                    menu['full_key'] = parent_key + '_' + menu.get('key')
                else:
                    menu['full_key'] = menu.get('key')
                data.append(menu)
                if 'submenu' in menu.keys():
                    Menu.getMenuPath(menu.get('submenu'), keys, data,
                                     menu['full_key'])

        return data

    # 获取key的配置信息
    def getMenuConfig(config, key):
        menu = config.get('MENU')
        keys = key.split('.')

        data = []
        for k, v in enumerate(keys):
            if menu.get(v) is None:
                raise Exception("配置错误" + key)
            data.append(menu[v])
            if menu.get(v).get('submenu') is not None:
                menu = menu[v]['submenu']

        return data
