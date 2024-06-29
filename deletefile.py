import os
from getfile import AddNews


def deleteFile():
    # 指定要删除的文件路径列表
    file_paths = [
        'dict_news.json',
        'data1.json',
        'data2.json',
    ]

    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error deleting file {file_path}: {e.strerror}")
        else:
            print(f"File {file_path} does not exist.")

        # 调用函数以删除文件


if __name__ == '__main__':
    deleteFile()
    AddNews()
