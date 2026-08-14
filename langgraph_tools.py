from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain.tools import tool
import requests
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

load_dotenv()

#=====search_engine tool======

search_engine = TavilySearch(
    max_results = 3,
    topic="general"
)

#====documentation scrapper====
@tool

def documentation_scrapper(url:str):
    """
    Scrapes a given web tutorial, documentation page, or blog URL and returns clean Markdown.
    Use this tool to evaluate whether an article or document matches the user's difficulty level and preferences.
    """
    try:
        jina_url = f"https://r.jina.ai/{url}"
        headers = {"User-agent":"AI_AdaptivelearningWeb/0.1"} 
        response = requests.get(jina_url,headers=headers,timeout=30)
        
        if response.status_code == 200:
            return response.text[:3000]
        return f"failed to scrape the content:HTTP status code:{response.status_code}"
    
    except Exception as error:
        return f"failed to scrape the content: {str(error)}"
    
    
#=====youtube search and transcript tool=====
@tool
def youtube_scrapper(search_query:str):
    """Searches youTube and returns titles, URLs, and transcripts for up to 3 videos."""
    try:
        videos = scrapetube.get_search(search_query,limit=3)
        video_list = list(videos)
        
        if not video_list:
            return f"videos on the '{search_query}' is not available"
        
        results = []
        
        for index,video in enumerate(video_list,1):
            video_id = video["videoId"]
            title = video.get("title", {}).get("runs",[{}])[0].get("text","title_is_not_available")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            try:
                video_transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=['en','en-US','en-GB'])
                full_transcript = " ".join([Short_transcript["text"] for Short_transcript in video_transcript])
                transcript_snippet = full_transcript[:800]
                
            except Exception:
                transcript_snippet ="(Transcript is not available for this video)"
                
            results.append(
                f"video {index}:\nTitle: {title}\nURL:{video_url}\ntranscript:{transcript_snippet}\n"
            )
            
        return "\n=====\n".join(results)
        
    except Exception as error:
        return f"Error searching for youtube video for '{search_query}:{str(error)}"
    

#=====youtube link extractor ======
@tool
def youtube_video_content(youtube_url:str):
    """Extracts metadata (title, author) and transcript text from a direct YouTube link."""
    
    try:
        yt = YouTube(youtube_url)
        video_id = yt.video_id
        title = yt.title
        channel = yt.author
        
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id,languages=['en','en-US','en-GB'])
        full_transcript = " ".join([Short_transcript["text"] for Short_transcript in transcript_data])
        transcript_snippet = full_transcript[:1500]
        return f"title:{title}\nchannel:{channel}\ntranscipt:{transcript_snippet}"
    
    except Exception as error:
        return f"Error 'can't able to read given link content' :{str(error)} "
        

#=====finally tool binding======
all_tools = [search_engine,youtube_scrapper,documentation_scrapper,youtube_video_content]
    


    