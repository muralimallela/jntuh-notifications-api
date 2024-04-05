from fastapi import FastAPI, Query,status
from bs4 import BeautifulSoup
import requests
import re
import uvicorn
from os import getenv

app = FastAPI()

@app.get("/",status_code=status.HTTP_200_OK)
def root():
    return {"message" : "visit URL/docs for api documentation"}
@app.get("/notifications",status_code=status.HTTP_200_OK)
async def fetch_data(query: str = Query(None)):
    url = "http://61.1.174.28/jsp/RCRVInfo.jsp"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            h3_tags = soup.find_all('h3')
            content = []
            for h3_tag in h3_tags:
                text = h3_tag.text.strip()
                content.append(text)
            string_list = content
            pattern = r'\*?\((.*?)\)\s+(.*?)\.+\s+LAST DATE TO APPLY FOR\s+(.*?):\s+(\d{2}-\d{2}-\d{4})'
            result_list = []
            for string in string_list:
                match = re.match(pattern, string)
                if match:
                    release_date = match.group(1)
                    notification = match.group(2)
                    end_date = match.group(4)
                    result = {
                        "release_date": release_date,
                        "notification": notification,
                        "warning": f"Last date to apply for {match.group(3)} is {end_date}"
                    }
                    result_list.append(result)
            if query:
                filtered_results = [result for result in result_list if query.lower() in result['release_date'].lower() or query.lower() in result['notification'].lower() or query.lower() in result['warning'].lower()]
                return filtered_results
            else:
                return result_list
        else:
            return {"message": f"Failed to fetch the HTML content. Status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"message": f"Error fetching the HTML content: {e}"}


if __name__ == "__main__":
    port = int(getenv("PORT",8000))
    uvicorn.run("main:app",host="0.0.0.0",port=port,reload=True)