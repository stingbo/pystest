# coding = utf-8


class Menu:
    # 获取key的配置信息
    def getMenuConfig(self, config, key):
        menus = config.get('MENU')
        keys = key.split('.')
        data = []
        return self.getMenuByKey(menus, keys, data)

    def getMenuByKey(self, menus, keys, data):
        for i, test_case in enumerate(keys):
            if test_case not in menus.keys():
                raise Exception('配置错误' + test_case)

            if (i + 1) == len(keys):
                menu = menus.get(test_case)
                # 配置的最后项则需要判断是否还有后续菜单，有则获取所有submenu内容执行
                if 'submenu' in menu.keys():
                    copy_menu = menu.copy()
                    del copy_menu['submenu']
                    data.append(copy_menu)
                    self.getSubmenu(menu, data)
                else:
                    data.append(menu)
            else:
                menu = menus.get(test_case)
                if 'submenu' in menu.keys():
                    copy_menu = menu.copy()
                    del copy_menu['submenu']
                    data.append(copy_menu)
                    menus = menu.get('submenu')
        return data

    # 递归获取下级所有submenu
    def getSubmenu(self, menus, data):
        if 'submenu' in menus.keys():
            submenus = menus.get('submenu')
            keys = submenus.keys()
            for i, test_case in enumerate(keys):
                sm = submenus.get(test_case)
                copy_sm = sm.copy()
                if 'submenu' in submenus.get(test_case).keys():
                    del copy_sm['submenu']
                    data.append(copy_sm)
                    self.getSubmenu(sm, data)
                else:
                    data.append(copy_sm)
        return data
