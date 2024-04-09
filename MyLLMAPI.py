from claude_api import Client
class MyLLMAPI:
    def __init__(self,file_folder:str):
        self.error_message = ''
        self.cookie = ''
        self.uuid_title = ''
        self.uuid_conclusion=''

        self.readCookie(file_folder)
        self.readUUID(file_folder)

        self.client = Client(self.cookie)
    def readCookie(self, file_path:str) -> None:
        with open(file_path + 'claude-ai-cookie.txt', 'r') as f:
            self.cookie = f.read()
        if self.cookie == '':
            raise Exception('cookie is empty')
        
    def readUUID(self, file_path:str) -> None:
        with open(file_path + 'claude-ai-uuid-title_fixer.txt', 'r') as f:
            self.uuid_title = f.read()
        with open(file_path + 'claude-ai-uuid-conclusion.txt', 'r') as f:          
            self.uuid_conclusion = f.read()

        if self.uuid_title == '' or self.uuid_conclusion == '': 
            raise Exception('uuid is empty')

    def getAnswer(self, prompt: str,uuid) -> str:
        return self.client.send_message(prompt, uuid)
    
    def getORGNameByPrompt(self, prompt: str) -> str:
        return self.getAnswer(prompt,self.uuid_title)

    def getDepartmentsByPrompt(self, prompt: str) -> str:
        return self.getAnswer(prompt,self.uuid_conclusion)

class MyTitleFixerLLMAPI(MyLLMAPI):
    def __init__(self,file_path):
        super(MyTitleFixerLLMAPI,self).__init__(file_path)
    def sendORGStartPrompt(self) -> str:
        raise Exception('Please don\'t use this function because the model claude-2.0 doesnt have memory')
        response = self.client.send_message('你的任務是幫我判斷是哪個公司在招人，回答形式請回傳 \"數字.公司名稱\" 不要廢話,請使用繁體中文,若無公司名稱公司名稱寫Unknown,之間不要有空格\n', self.uuid)
        return response
    def fixListIfNoneTitle(self,titles_after_tokenization:list,raw_titles:list) -> list:
        
        prompt_message_initial = "你的任務是幫我判斷是哪個公司在招人，回答形式請回傳 \"數字.公司名稱\" 不要廢話,請使用繁體中文,若無公司名稱公司名稱寫Unknown,之間不要有空格, Let\'s think step by step\n"
        prompt_message = prompt_message_initial
        to_change_list = []
        prompt_message_split = []
        number = 0
        print(titles_after_tokenization)
        input("Let's stop for a sec")
        for title in titles_after_tokenization:
            if title == 'None':
                prompt_message_split.append(f'{number}.{raw_titles[number]}\n')
                # prompt_message += f'{number}.{raw_titles[number]}\n'
                to_change_list.append(number)
            number+=1
        # print(to_change_list)
        # input("Let's stop for a sec")

        if to_change_list != []:
            segement_company = 15
            start_index = 0
            for i in range(len(to_change_list)//segement_company):
                prompt_message = prompt_message_initial + '\n'.join([str(x) for x in prompt_message_split[i*segement_company:(i+1)*segement_company]])
                response_message = self.getORGNameByPrompt(prompt_message)
                print(response_message)
                tmp_titles = response_message.split('\n')
                print(tmp_titles)
                result_list_after_fix = []
                for j in range(len(tmp_titles)):
                    number = tmp_titles[j][0:tmp_titles[j].find('.')]
                    new_title = tmp_titles[j][tmp_titles[j].find('.')+1:]
                    if number == '':
                        continue
                    number = int(number)
                    
                    #between start end has title
                    for num in range(start_index,number,1):
                        result_list_after_fix.append(titles_after_tokenization[num])

                    result_list_after_fix.append(new_title)
                    start_index = number+1
            return result_list_after_fix
        
        return titles_after_tokenization





if __name__ == '__main__':
    api = MyLLMAPI('./api-assets/')

    result = api.client.send_message("Sorry, I sent to many messages, can you be more polite?",conversation_id="01277297-3cb8-4b61-8cc6-b6e4ef9bfd7d")

    # print(api.getORGNameByPrompt('嗨! 我會給你一段文字，請你幫我判斷是哪個公司在招人，回答形式請回傳 \"公司名稱:\" 不要廢話\n 【轉知】德州儀器首場女性專場徵才說明會報名開跑！'))