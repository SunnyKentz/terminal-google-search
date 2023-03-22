from enum import Enum
import sys
import requests
import webbrowser
import readchar

class Result(Enum):
    no_result = 0
    quick_result = 1
    quick_website_result = 2
    FAQ = 3
    normal_result = 4

class SearchResult:
    def __init__(self,resultType:int):
        self.resultType = Result.no_result
        self.title = ""
        self.answer = ""
        self.website = ""
    
    def setTitle(self,title:str):
        self.title = title
    
    def setAnswer(self,title:str):
        self.answer = title

    def setWebsite(self,title:str):
        self.website = title

    def setResultType(self,rt=Result.no_result):
        self.resultType = rt

    def print(self):
        print("\033[96m************************************************************************")
        print(f"\033[94m{self.title}")
        print("\033[96m------------------------------------------------------------------------")
        print("\033[0m" + formatIntoParagraph(self.answer))
        print("\033[0m["+self.website+"]")
        print("************************************************************************\n\n")

def formatIntoParagraph(string:str)->str:
    paragraph = "    "

    i = 0
    while True:
        try:
            j = i+72
            if string[j] == " ":
                pass
            else:
                while string[j] != " ":
                    j-=1
                j +=1
            paragraph = paragraph + string[i:j] + "\n    "
            i = j
        except:
            paragraph = paragraph + string[i:]
            break

    return paragraph

def formatSearchSubject(searchSubject:list)-> list:
    readableArgsArray = searchSubject
    readableArgsArray.pop(0)
    
    return readableArgsArray

def formatUrl(readableArgs:list,page:int)-> str:
    formatedUrl = ""
    for i in range(len(readableArgs)):
        formatedUrl = formatedUrl + readableArgs[i]
        if not i+1 == len(readableArgs):
            formatedUrl = formatedUrl + "+"
    formatedUrl = formatedUrl + "&start="+str(page)
    return formatedUrl

def getHtml(searchUrl:str)->str:
    response_API = requests.get('https://www.google.com/search?q='+searchUrl)
    print(response_API.status_code, "\n")

    return response_API.text

def findQuickResult(resultList:list)->list:
    return []

def findQuickWebsiteResult(resultList:list)->list:
    return []

def findTitle(div:str)->str:

    title = ""
    start = 0
    end = 0

    for i in range(len(div)):

        if div[i] == ">" and div[i+1] != "<":
            start = i
            break
        
    for i  in range(start,len(div)):
        if div[i] == "<":
            end = i
            break
    title = div[start:end]

    formatedAnswer = removeUnwantedChars(title)

    return formatedAnswer

    return title

def findAnswer(divs:list,resultType:int,index:int)->str:
    
    answer = ""

    start = 0
    end = 0

    if resultType == Result.normal_result:
        div = divs[index+3]
        for k in range(4):
            try:
                for i in range(end,len(div)):
                    
                    if div[i] == ">" and div[i+1] != "<":
                        start = i+1
                        break
                for i  in range(start,len(div)):
                    if div[i] == "<":
                        end = i
                        break
                answer = answer + div[start:end]
            except:
                break
    formatedAnswer = removeUnwantedChars(answer)
    return formatedAnswer

def removeUnwantedChars(answer:str)->str:
    formatedAnswer = ""
    for line in answer.split():
        new_words = ' '.join([word for word in line.split() if not any([phrase in word for phrase in ["&#","&gt;","&amp;"]])])
        formatedAnswer = formatedAnswer + new_words + " "
    return formatedAnswer

def findWebsite(divs:list,resultType:int,index:int)->str:

    website = ""
    start = 0
    end = 0

    if resultType == Result.normal_result:
        div = divs[index]
        for i in range(len(div)-1,0,-1):
            if div[i] == "<" and div[i-1] != ">":
                end = i-1
                break
        for i  in range(end,0,-1):
            if div[i] == ">":
                start = i+1
                break
        fullWebsite  = div[start:end]
        website = div[start:end].split()[0]

    return website

def findFAQ(resultList:list)->list:
    return []

def findNormalResults(resultList:list)->list:
    normalResults = []
    for i in range(0,len(resultList)-1):
        if '<div class="Gx5Zad fP1Qef xpd EtOod pkphOe">' in resultList[i]:
            normalResult = SearchResult(Result.normal_result)
            normalResult.setTitle(findTitle(resultList[i]))
            normalResult.setAnswer(findAnswer(resultList,Result.normal_result,i))
            normalResult.setWebsite(findWebsite(resultList,Result.normal_result,i))

            normalResults.append(normalResult)
    return normalResults

def formatHtml(htmlText:str)->list:

    with open("newHtml.html","w") as f:
        f.write(htmlText)
        f.close()

    bodyText = htmlText.split("<div>")
    bodyText.pop(0)
    
    try:
        for i in range(0,len(bodyText)-1):
            if len(bodyText[i])>2000:
                bodyText.pop(i)
    except:
        pass

    # for i in bodyText:print(i,"\n"+"-------------------------------------------------")

    arrayOfResults = []
    arrayOfResults.extend(findQuickResult(bodyText))
    arrayOfResults.extend(findQuickWebsiteResult(bodyText))
    arrayOfResults.extend(findNormalResults(bodyText))
    arrayOfResults.extend(findFAQ(bodyText))

    return arrayOfResults

def printResult(resultList:list,searchSubject:str):

    for j in resultList:
        j.print()

    print("press Ctrl-c to quit, press <Any> for next page, press <B> to open browser...")
    
    
    try:
        i = 10
        while True:
            searchUrl = formatUrl(searchSubject,i)
            
            option = readchar.readkey()
            if option == 'b':
                webbrowser.open('https://www.google.com/search?q='+searchUrl)
                break
            
            htmlTxt= getHtml(searchUrl)
            resultList = formatHtml(htmlTxt)

            for j in resultList:
                j.print()

            print("press Ctrl-c to quit, press <Any> for next page, press <B> to open browser...")

            i+=10
    except:
        print("\n")

if __name__ == "__main__":
    
    searchSubject = formatSearchSubject(sys.argv)
    searchUrl = formatUrl(searchSubject,0)
    htmlTxt= getHtml(searchUrl)
    resultList = formatHtml(htmlTxt)
    printResult(resultList,searchSubject)
    
    
