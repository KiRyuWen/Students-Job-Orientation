from claude_api import Client
class MyLLMAPI:
    def __init__(self,cookie_path,uuid_path):
        self.error_message = ''
        self.cookie = ''
        self.uuid = ''

        self.readCookie(cookie_path)
        self.readUUID(uuid_path)
        self.client = Client(self.cookie)
    def readCookie(self, file_path:str) -> None:
        with open(file_path, 'r') as f:
            self.cookie = f.read()
        if self.cookie == '':
            raise Exception('cookie is empty')
        
    def readUUID(self, file_path:str) -> None:
        with open(file_path, 'r') as f:
            self.uuid = f.read()
        if self.uuid == '':
            raise Exception('uuid is empty')

    def getAnswer(self, prompt: str) -> str:
        return self.client.send_message(prompt, self.uuid)
    
    def getORGNameByPrompt(self, prompt: str) -> str:
        response = self.getAnswer(prompt)
        return response

class MyTitleFixerLLMAPI(MyLLMAPI):
    def __init__(self,cookie_path,uuid_path):
        super(MyTitleFixerLLMAPI,self).__init__(cookie_path,uuid_path)
    def sendORGStartPrompt(self) -> str:
        raise Exception('Please don\'t use this function because the model claude-2.0 dont have memory')
        response = self.client.send_message('你的任務是幫我判斷是哪個公司在招人，回答形式請回傳 \"數字.公司名稱\" 不要廢話,請使用繁體中文,若無公司名稱公司名稱寫Unknown,之間不要有空格\n', self.uuid)
        return response
    def fixListIfNoneTitle(self,titles_after_tokenization:list,raw_titles:list) -> list:
        
        prompt_message = "你的任務是幫我判斷是哪個公司在招人，回答形式請回傳 \"數字.公司名稱\" 不要廢話,請使用繁體中文,若無公司名稱公司名稱寫Unknown,之間不要有空格, Let\'s think step by step\n"
        to_change_list = []
        number = 0
        for title in titles_after_tokenization:
            if title == 'None':
                prompt_message += f'{number}.{raw_titles[number]}\n'
                to_change_list.append(number)
            number+=1


        if to_change_list != []:
            response_message = self.getORGNameByPrompt(prompt_message)
            tmp_titles = response_message.split('\n')

            result_list_after_fix = []
            start_index = 0
            for i in range(len(tmp_titles)):
                number = tmp_titles[i][0:tmp_titles[i].find('.')]
                new_title = tmp_titles[i][tmp_titles[i].find('.')+1:]
                number = int(number)
                
                #between start end has title
                for num in range(start_index,number,1):
                    result_list_after_fix.append(titles_after_tokenization[num])

                result_list_after_fix.append(new_title)
                start_index = number+1
            return result_list_after_fix
        
        return titles_after_tokenization





if __name__ == '__main__':
    api = MyLLMAPI('./api-assets/claude-ai-cookie.txt','./api-assets/claude-ai-uuid.txt')
    # print(api.getORGNameByPrompt('嗨! 我會給你一段文字，請你幫我判斷是哪個公司在招人，回答形式請回傳 \"公司名稱:\" 不要廢話\n 【轉知】德州儀器首場女性專場徵才說明會報名開跑！'))