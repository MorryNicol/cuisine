#导入第三方库 
import random
#读取文件
import pandas as pd  
# from playwright.sync_api import sync_playwright as playwright
# 设置让 Pandas 打印时避免截断内容  
pd.set_option('display.max_colwidth', None)  


# 直接从文件读取 JSON 并转换为 DataFrame  
df = pd.read_json("food_data.json")  

# 从网络上重新获取图片
def get_img(cai_names):
    src_list = []
    with playwright() as pw:
        Headless = True
        webkit = pw.webkit.launch(headless=Headless)
        user_agent_random = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/524.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
        context = webkit.new_context(user_agent=user_agent_random)  
        page = context.new_page()  # 创建一个新的页面
        for cai_name in cai_names:
            try:
                page.goto(f'https://cn.bing.com/images/search?q={cai_name}')
            except:
                webkit.close()
                webkit = pw.webkit.launch(headless=Headless)
                context = webkit.new_context(user_agent=user_agent_random)  
                page = context.new_page()  # 创建一个新的页面
                page.goto(f'https://cn.bing.com/images/search?q={cai_name}')
            images = page.locator('img')
            image = images.nth(1)
            src = image.get_attribute('src')
            src_list.append(src)
        webkit.close()
    return src_list

def match_ingredient(ingredient_value, ingredient_list):  
    """  
    判断 ingredient_list 是否完全包含于 ingredient_value 中。  

    参数:  
        ingredient_value (list): 要匹配的 ingredient 值列表。  
        ingredient_list (list): 某行 ingredients_list 列中包含的列表。  

    返回:  
        bool: 如果 ingredient_list 的所有元素都包含在 ingredient_value 中，返回 True；否则返回 False。  
    """  
    return set(ingredient_list).issubset(set(ingredient_value)) 


def search_food(ingredient_value, flavor_value='', click_time=None):  
    """  
    根据 ingredient 和 flavor 的值筛选数据，并返回筛选后的结果列表。  

    参数:  
        df (pd.DataFrame): 数据表  
        ingredient_value (list): 包含所有 ingredients 的列表  
        flavor_value (str or None): 要匹配的 flavor 值，如果为 None，则不限制 flavor 的匹配  
    
    返回:  
        list: 包含筛选结果的列表，每个元素是一个字典，包含 'title', 'steps', 'image'  
    """  
    try:  
        # 筛选条件：检查 ingredients_list 是否完全包含于 ingredient_value  
        ingredient_match = df['ingredients_list'].apply(lambda x: match_ingredient(ingredient_value, x))  
        
        # 检查 flavor_value 是否存在并做筛选  
        if flavor_value != '':  # 如果 flavor_value 不为 None，则基于 flavor 进一步筛选  
            filtered_df = df[ingredient_match & (df['flavor'].apply(lambda x: flavor_value in x))]  
        else:  # 如果未提供 flavor_value，则不限制 flavor  
            filtered_df = df[ingredient_match]  

        filtered_df['len'] = filtered_df['ingredients_list'].apply(len)
        sorted_df = filtered_df.sort_values(by='len',ascending=False)

        result_df = sorted_df.loc[sorted_df['steps'].apply(lambda x: len(x)>0),]

        if click_time==None:
            result_df = result_df.iloc[:10,]
        else:
            result_df = result_df.iloc[click_time*10:(click_time+1)*10,]
        # result_df['image'] = get_img(result_df['title'])
        
        return result_df[['title','ingredients_list','image','steps']]  # 提取所需列返回  

    except KeyError as e:  
        print(f"Error: Column not found - {str(e)}")  
        return []  



# # 加载并转化为列表  
# # ingredient_value =  ['牛肉片', '青椒片', '淀粉', '味精','西红柿','土豆','茄子', '番茄', '肉糜'] 
# ingredient_value = ['鸡腿肉','胡萝卜','鸡蛋','芥蓝','茄子','青椒','番茄','南瓜','香菇','平菇','木耳'] 
# search_result = search_food(ingredient_value=ingredient_value )
# for index, row in search_result.iterrows():  
#     print(f"Title: {row['title']}")  
#     print(f"Ingredients_list: {row['ingredients_list']}")  
#     print(f"Steps: {row['steps']}")  
#     print(f"Image Path: {row['image']}")      
#     print("-" * 40)  # 分隔每一条结果  

# search_result.to_json('sample_food.json')

# def search_food(ingredient_value, flavor_value='', click_time=None): 
#     return pd.read_json('sample_food.json')