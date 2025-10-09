"""
SQL模板模块

该模块提供可扩展的SQL模板系统，其他模块可以直接调用模板进行填充。
"""

from string import Template
from typing import Dict, Any, Optional


class SQLTemplates:
    """
    SQL模板管理类，提供常用的SQL查询模板
    """

SELECT "摘要" 
FROM datalist 
WHERE "申请人" LIKE '%台灣積體電路製造股份有限公司%' 
  AND "专利名" LIKE '%半導體製造方法%' 
LIMIT 2;

SELECT COUNT(*) 
FROM datalist 
WHERE "申请人" LIKE '%台灣積體電路製造股份有限公司%' 
  AND "专利名" LIKE '%半導體%' 
  AND strftime('%Y', replace("公开日期", '/', '-')) = '2024';

SELECT strftime('%Y', replace("公开日期", '/', '-')) AS year, COUNT(*) AS patent_count 
FROM datalist 
WHERE "申请人" LIKE '%台灣積體電路製造股份有限公司%' 
  AND strftime('%Y', replace("公开日期", '/', '-')) BETWEEN '2020' AND '2024' 
GROUP BY year 
ORDER BY patent_count DESC 
LIMIT 1;

SELECT "发明人" 
FROM datalist 
WHERE "申请人" LIKE '%台灣積體電路製造股份有限公司%' 
  AND "专利名" LIKE '%記憶體電路及其操作方法%';

SELECT "摘要" 
FROM datalist 
WHERE "申请人" LIKE '%台灣積體電路製造股份有限公司%' 
  AND "专利名" LIKE '%記憶體電路及其操作方法%';


    # 基础查询模板
    BASE_SELECT = Template('SELECT $fields FROM datalist WHERE 1=1$conditions;')
    
    # 常用查询模板
    BY_APPLICANT = Template('SELECT $fields FROM datalist WHERE "申请人" LIKE \'%$applicant%\'$conditions;')
    BY_YEAR = Template('SELECT $fields FROM datalist WHERE "公开日期" LIKE \'%$year%\'$conditions;')
    BY_PATENT_NAME = Template('SELECT $fields FROM datalist WHERE "专利名" LIKE \'%$patent_name%\'$conditions;')
    BY_PATENT_ID = Template('SELECT $fields FROM datalist WHERE "公开号" LIKE \'%$patent_id%\'$conditions;')
    BY_INVENTOR = Template('SELECT $fields FROM datalist WHERE "发明人" LIKE \'%$inventor%\'$conditions;')
    
    # 组合查询模板
    BY_APPLICANT_AND_YEAR = Template(
        'SELECT $fields FROM datalist WHERE "申请人" LIKE \'%$applicant%\' AND "公开日期" LIKE \'%$year%\'$conditions;'
    )
    
    # 聚合查询模板
    COUNT_BY_APPLICANT = Template(
        'SELECT COUNT(*) FROM datalist WHERE "申请人" LIKE \'%$applicant%\'$conditions;'
    )
    COUNT_BY_YEAR = Template(
        'SELECT COUNT(*) FROM datalist WHERE "公开日期" LIKE \'%$year%\'$conditions;'
    )


def fill_template(template: Template, **kwargs) -> str:
    """
    填充SQL模板
    
    Args:
        template: Template对象
        **kwargs: 模板参数
        
    Returns:
        str: 填充后的SQL语句
    """
    return template.substitute(**kwargs)


def build_conditions(**conditions) -> str:
    """
    构建WHERE条件子句，全部使用模糊查询
    
    Args:
        **conditions: 条件字典，如 {"申请人": "日立化成", "年份": "2003"}
        
    Returns:
        str: 构建好的条件字符串
    """
    condition_str = ""
    for field, value in conditions.items():
        condition_str += f' AND "{field}" LIKE \'%{value}%\''
            
    return condition_str


# 使用示例
if __name__ == "__main__":
    # 示例1: 根据申请人查询专利名称
    sql1 = fill_template(
        SQLTemplates.BY_APPLICANT, 
        fields='"专利名"', 
        applicant='日立化成工業股份有限公司',
        conditions=build_conditions(公开日期='2003')
    )
    print("示例1:", sql1)
    
    # 示例2: 根据申请人和年份查询
    sql2 = fill_template(
        SQLTemplates.BY_APPLICANT_AND_YEAR,
        fields='"专利名"',
        applicant='台灣積體電路製造股份有限公司',
        year='2024',
        conditions=''
    )
    print("示例2:", sql2)
    
    # 示例3: 统计数量
    sql3 = fill_template(
        SQLTemplates.COUNT_BY_APPLICANT,
        applicant='台灣積體電路製造股份有限公司',
        conditions=build_conditions(公开日期='2024')
    )
    print("示例3:", sql3)