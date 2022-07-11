import os


def start():
    forum_soft = input("Enter software name on which forum is working\nPossible variants:\n\t1.Xceref\n\t2.phpBB\n\t3.Other\nEnter name or number:")

    if forum_soft == 'Xceref' or forum_soft == '1':
        os.system('py Xceref.py')
        exit()
    elif forum_soft == 'phpBB' or forum_soft == '2':
        os.system('py phpBB.py')
        exit()
    elif forum_soft == 'Other' or forum_soft == '3':
        os.system('py others.py')
    else:
        print("You didn't enter right parameter, please enter one of the avaible variants.")

if __name__ == '__main__':
    start()