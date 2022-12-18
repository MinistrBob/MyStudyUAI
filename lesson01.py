def del_from_tuple(tpl, elem):
    if elem not in tpl:
        return tpl
    else:
        t = list(tpl)
        t.remove(elem)
        return tuple(t)


def to_list(tpl):
    t = [tpl, ]
    return t


if __name__ == '__main__':
    # print(del_from_tuple((1, 2, 3), 1))
    # print(del_from_tuple((1, 2, 3, 1, 2, 3, 4, 5, 2, 3, 4, 2, 4, 2), 3))
    phrase = "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
    print('Количество символов во фразе до буквы "е":', phrase.find("е"))
    print(to_list(([1, 2, 3], 8.3, True, 'Строка')))
