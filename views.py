# from django.shortcuts import render
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# import json
# from pytube import YouTube
# from django.conf import settings
# import os
# import assemblyai as aai
# import openai
# from decouple import config
# from .models import BlogPost
# # Create your views here.
# @login_required
# def index(request):
#     return render(request, 'index.html')

# @csrf_exempt
# def generate_blog(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             yt_link = data['link']
#         except (KeyError, json.JSONDecodeError):
#             return JsonResponse({'error': 'Invalid data sent'}, status=400)
        
#         # get title
#         title = yt_title(yt_link)
#         # transcript
#         transcription = get_transcription(yt_link)
#         if not transcription:
#             return JsonResponse({'error': 'Transcription failed'}, status=500)
#         # openAI
#         blog_content = generate_blog_from_transcription(transcription)
#         if not blog_content:
#             return JsonResponse({'error': 'Failed to generate blog'}, status=500)
#         # save to db
#         new_blog_Article = BlogPost.objects.create(
#             user = request.user,
#             youtube_title = title,
#             youtube_link = yt_link ,
#             generated_content = blog_content,
#         )
#         new_blog_Article.save()
#         # return blog as response
#         return JsonResponse({'content': blog_content})
#     else:
#         return JsonResponse({'error': 'Invalid request'}, status=405)

# def yt_title(link):
#     yt = YouTube(link)
#     title = yt.title
#     return title

# def download_audio(link):
#     yt = YouTube(link)
#     video = yt.streams.filter(only_audio=True).first()
#     out_file = video.download(output_path=settings.MEDIA_ROOT)
#     base, ext = os.path.splitext(out_file)
#     new_file = base + '.mp3'
#     os.rename(out_file, new_file)
#     return new_file

# def get_transcription(link):
#     audio_file = download_audio(link)
#     aai.settings.api_key = config('ASSEMBLYAI_API_KEY')    
#     transcriber = aai.Transcriber()
#     transcript = transcriber.transcribe(audio_file)

#     return transcript.text

# def generate_blog_from_transcription(transcription):
#     openai.api_key = config('OPENAI_API_KEY')    
#     prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it like a proper blog article:\n\n{transcription}\n\nArticle:"
    
#     response = openai.Completion.create(
#         model = "text-davinci-003",
#         prompt = prompt,
#         max_tokens = 1000
#     )

#     generated_content = response.choices[0].text.strip()

#     return generated_content

# def blog_list(request):
#     blog_articles = BlogPost.objects.filter(user=request.user)
#     return render(request, "all-blogs.html", {'blog_articles': blog_articles})

# def blog_details(request, pk):
#     blog_article_detail = BlogPost.objects.get(id=pk)
#     if request.user == blog_article_detail.user:
#         return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
#     else:
#         return redirect('/')

# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('/')
#         else:
#             error_message = "Invalid username or password"
#             return render(request, 'login.html', {'error_message' : error_message})
#     return render(request, 'login.html')

# def user_signup(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         repeatPassword = request.POST['repeatPassword'] 

#         if password == repeatPassword:
#             try:
#                 user = User.objects.create_user(username, email, password)
#                 user.save()
#                 login(request, user)
#                 return redirect('/')
#             except:
#                 error_message = 'Error in creating account'
#                 return render(request, 'signup.html', {'error_message': error_message})
#         else:
#             error_message = "Password do not match"
#             return render(request, 'signup.html', {'error_message': error_message})
#     return render(request, 'signup.html')
    

# def user_logout(request):
#     logout(request)
#     return redirect('/')

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai as aai
import openai
from decouple import config
from .models import BlogPost


# Configure logging
logger = logging.getLogger(__name__)

@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            logger.error("Invalid data sent to generate_blog")
            return JsonResponse({'error': 'Invalid data sent'}, status=400)
        
        # get title
        try:
            title = yt_title(yt_link)
        except Exception as e:
            logger.error(f"Failed to fetch YouTube title: {e}")
            return JsonResponse({'error': 'Failed to fetch YouTube title'}, status=500)

        # transcript
        try:
            transcription = get_transcription(yt_link)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return JsonResponse({'error': 'Transcription failed'}, status=500)

        # openAI
        try:
            blog_content = generate_blog_from_transcription(transcription)
        except Exception as e:
            logger.error(f"Failed to generate blog content: {e}")
            return JsonResponse({'error': 'Failed to generate blog'}, status=500)

        # save to db
        try:
            new_blog_Article = BlogPost.objects.create(
                user=request.user,
                youtube_title=title,
                youtube_link=yt_link,
                generated_content=blog_content,
            )
            new_blog_Article.save()
        except Exception as e:
            logger.error(f"Failed to save blog post: {e}")
            return JsonResponse({'error': 'Failed to save blog post'}, status=500)

        # return blog as response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    try:
        yt = YouTube(link)
        title = yt.title
        return title
    except Exception as e:
        logger.error(f"Failed to fetch YouTube title: {e}")
        raise

def download_audio(link):
    try:
        print(f"Attempting to download audio from link: {link}")
        yt = YouTube(link)
        video = yt.streams.filter(only_audio=True).first()
        if not video:
            print(f"No audio stream found for link: {link}")
            return None
        out_file = video.download(output_path=settings.MEDIA_ROOT)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        return new_file
    except Exception as e:
        print(f"Failed to download YouTube audio: {e}")
        return None

def get_transcription(link):
    try:
        audio_file = download_audio(link)
        if not audio_file:
            print("Audio file download failed")
            return None

        # aai.settings.api_key = config('ASSEMBLYAI_API_KEY')
        transcriber = aai.Transcriber()

        # Open the audio file in binary mode
        with open(audio_file, 'rb') as f:
            transcript = transcriber.transcribe(f)
            print(f"Transcript received: {transcript.text[:100]}...")  # Log the first 100 characters
            return transcript.text

    except Exception as e:
        print(f"Transcription failed: {e}")
        return None

def generate_blog_from_transcription(transcription):
    try:
        # openai.api_key = config('OPENAI_API_KEY')
        prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but don't make it look like a YouTube video, make it like a proper blog article:\n\n{transcription}\n\nArticle:"
        
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1000
        )

        generated_content = response.choices[0].text.strip()
        return generated_content
    except Exception as e:
        logger.error(f"Failed to generate blog from transcription: {e}")
        raise

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message' : error_message})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error in creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = "Passwords do not match"
            return render(request, 'signup.html', {'error_message': error_message})
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
