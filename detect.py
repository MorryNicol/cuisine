# from model.notebooks.Mydetect import Mydetect
from Mydetect import Mydetect

def detect(picture_path):
    """
    输入待检测图片路径，输出检测结果

    Args:
        picture_path (string): 图片路径.

    Returns:
        list: 图片包含的菜，以列表形式返回.
    """
    ## food = ['番茄','土豆'] #用于测试
    # food = ['鸡腿肉','胡萝卜','鸡蛋','芥蓝','茄子','青椒','番茄','南瓜','香菇','平菇','木耳']
    food = Mydetect(picture_path)
    ## print(food)
    return food

# 测试代码
# path = input("请输入图片路径:\n")
# detect(path)