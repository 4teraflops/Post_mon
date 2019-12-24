
dictionary = {'key': 'val', 'key2': 'val2'}
lst = ["val", "val2", "val3"]

a = list(filter(lambda x: dictionary[x] in lst, dictionary))

print(a)

