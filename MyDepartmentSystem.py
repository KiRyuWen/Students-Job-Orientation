class MyDepartmentSystem:
    def __init__(self) -> None:
        self.department_list = [
            '機械工程系',
            '材料科學與工程系',
            '營建工程系',
            '化學工程系',
            '電子工程系',
            '電機工程系',
            '資訊工程系',
            '工業管理系',
            '企業管理系',
            '資訊管理系',
            '設計系',
            '建築系',
            '應用外語系',
            '經濟學系',

            '其他',
        ]
    def getDepartmentLists(self) -> list:
        return self.department_list

    