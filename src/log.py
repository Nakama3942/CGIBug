import os


class Log:
    _file = None
    _instance = None
    _editor = None

    @staticmethod
    def instance(editor=None):
        if Log._instance is None:
            filename = 'log.txt'
            try:
                os.remove(filename)
            except OSError:
                pass
            Log._instance = Log(filename, editor)
        return Log._instance

    def __init__(self, file, editor=None):
        self._file = open(file, 'w+')
        self._editor = editor

    @staticmethod
    def out(text):
        print(text)
        Log.instance()._file.write(text + "\n")
        if Log.instance()._editor is not None:
            Log.instance()._editor.append(text)


if __name__ == '__main__':
    Log.out("test1")
    Log.out("test2")
