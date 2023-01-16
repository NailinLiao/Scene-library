def json_2_mask():
    import os

    json_folder = r"C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\small_img"
    #  获取文件夹内的文件名
    FileNameList = os.listdir(json_folder)
    #  激活labelme环境
    os.system("activate labelme")
    for i in range(len(FileNameList)):
        #  判断当前文件是否为json文件
        if (os.path.splitext(FileNameList[i])[1] == ".json"):
            json_file = json_folder + "\\" + FileNameList[i]
            #  将该json文件转为png
            os.system("labelme_json_to_dataset " + json_file)


def transfer_file():
    import os
    import shutil

    png_folder = r"C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\save_path\small_img"
    Paste_png_folder = r"./save_path/train/img"
    Paste_label_folder = r"./save_path/train/label"
    #  获取文件夹内的文件名
    FileNameList = os.listdir(png_folder)
    NewFileName = 1
    for i in range(len(FileNameList)):
        #  判断当前文件是否为json文件
        if (os.path.splitext(FileNameList[i])[1] == ".png"):
            #  复制png文件
            png_file = png_folder + "\\" + FileNameList[i]
            new_png_file = Paste_png_folder + "\\" + str(NewFileName) + ".png"
            print(png_file)
            print(new_png_file)

            #  复制label文件
            png_file_name = FileNameList[i].split(".", 1)[0]
            label_file = png_folder + "\\" + png_file_name + "_json\\label.png"
            new_label_file = Paste_label_folder + "\\" + str(NewFileName) + ".png"
            try:
                shutil.copyfile(label_file, new_label_file)
                shutil.copyfile(png_file, new_png_file)

            except:
                pass
            #  文件序列名+1
            NewFileName = NewFileName + 1


def up_all_file():
    import shutil
    import os
    tar_img_path = r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\Data_tools\DataSet\est\img3'
    tar_label_path = r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\Data_tools\DataSet\est\label3'

    base_file = r'C:\Users\NailinLiao\PycharmProjects\CameraStatusCheck\Data_tools\DataSet\train'
    save_img_path = os.path.join(base_file, 'img')
    save_label_path = os.path.join(base_file, 'label')
    save_path_img_list = os.listdir(save_img_path)

    tar_imgs = os.listdir(tar_img_path)
    tar_labels = os.listdir(tar_label_path)

    for index, name in enumerate(tar_imgs):
        img_file_ = os.path.join(tar_img_path, name)
        label_file_ = os.path.join(tar_label_path, name)

        name = str(len(save_path_img_list) + index + 1) + '.png'
        new_img_file_ = os.path.join(save_img_path, name)
        new_label_file_ = os.path.join(save_label_path, name)

        print(img_file_)
        print(new_img_file_)
        shutil.copyfile(img_file_, new_img_file_)
        shutil.copyfile(label_file_, new_label_file_)


if __name__ == '__main__':
    transfer_file()
