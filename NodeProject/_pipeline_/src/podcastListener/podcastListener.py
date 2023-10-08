import os, shutil, subprocess, tempfile, json, sys
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

base_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = tempfile.gettempdir()

src_dir = os.sep.join(base_dir.split(os.sep)[:-1])
site_package_dir = src_dir + os.sep + 'site-packages'
if not site_package_dir in sys.path:
    sys.path.insert(0, site_package_dir)
import speech_recognition as sr
import feedparser, requests, parser

cache_dir = base_dir + '/cache'
transcription_dir = base_dir + '/cache/transcriptions'
csv_path = cache_dir + '/podcast_episode.csv'

class util:
    @staticmethod
    def is_internet_connect(url='https://google.com'):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                print("Request successful!")
                return True
            else:
                print(f"Request failed with status code: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print("Request timed out. Please check your network connection.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return False

class plistener ():
    def __init__(self, podcast_rss):
        self.podcast_rss = podcast_rss

    def get_feed_df(self, filter_url=None):
        '''
        :param filter_url: 'http://rustyanimator.com/blog/feed/'
        :return:
        '''
        global podcast_rss
        con_rss = []
        for u in list(podcast_rss):
            if filter_url != None:
                if not u == filter_url: continue
            if util.is_internet_connect(url=u):
                con_rss.append(u)

        df = pd.DataFrame([])
        for url in con_rss:
            if filter_url != None:
                if not url == filter_url: continue
            print(url)
            dp = feedparser.parse(url)
            rec = dp.entries
            rec = rec[:10]
            import pprint
            pprint.pprint(rec)

            for d in rec:
                print(d)
                data = {}
                for k in podcast_rss[url]:
                    p = d
                    for i in range(len(podcast_rss[url][k])):
                        p = p[podcast_rss[url][k][i]]
                        print('finding...' , k, p)

                    p = p.replace('<p>', '').replace('</p>', '').replace('amp;', '')
                    p = p.replace('<p dir="ltr">', '').replace('<span style=\"font-size: 10pt;\">', '')
                    p = p.replace('<span style=\"font-weight: 400;\">', '').replace('<h4>', '').replace('/<h4>', '')
                    p = p.replace('<span style=\"font-weight: 400; font-size: 10pt;\">', '').replace('</span>', '')
                    p = p.replace('\"', '').replace('\'', '').replace('#', '').replace('!', '')
                    for i in range(10):
                        p = p.replace('  ', ' ')
                    print(k, p)
                    data[k] = p.strip()

                df = df.append(pd.DataFrame([data]))

        '''
            for i, e in enumerate(dp.entries):
                one_feed = {}
                one_feed['etitle'] = e.title if 'title' in e else f'title {i}'
                one_feed['summary'] = e.summary if 'summary' in e else f'no summary {i}'
                one_feed['elink'] = e.link if 'link' in e else f'link {i}'
                one_feed['published'] = e.published if 'published' in e else f'no published {i}'
                one_feed['elink_img'] = e.links[1].href if 'links' in e and len(e.links)>1 else f'no link_img {i}'
    
                df = df.append(pd.DataFrame([one_feed]), ignore_index=True)
    
        #print('empty ', df.empty)
        '''

        df.reset_index(inplace=True, drop=True)
        return df

    def get_all_feed_df(self):
        while True:
            feed_df = self.get_feed_df()
            if not feed_df.empty:
                import time
                time.sleep(5)
                os.system('cls||clear')
                print(feed_df)
                return feed_df
                #break

    def transcription(self, file_path, txt_path):
        if not file_path.endswith('.mp3') or not txt_path.endswith('.txt'):
            return
        #mp3_path = r"C:\Users\DEX3D_I7\Downloads\y2mate.com - Realtime vs Offline 3d Rendering for Animation.mp3"
        mp3_path = file_path
        mp3_path = os.path.abspath(mp3_path)
        wav_dir = temp_dir + os.sep + os.path.basename(mp3_path).split('.')[0] + '_split'
        #wav_dir = os.path.dirname(mp3_path) + os.sep + os.path.basename(mp3_path).split('.')[0] + '_split'
        base_wav_path = wav_dir + os.sep + os.path.basename(mp3_path.replace('.mp3', '.wav'))
        if os.path.exists(wav_dir):
            try:shutil.rmtree(wav_dir)
            except:pass
        if not os.path.exists(wav_dir):
            os.mkdir(wav_dir)
            os.chmod(wav_dir, 0o777)

        path_to_ffmpeg_exe = path_to_ffmpeg_exe = os.sep.join(base_dir.split(os.sep)[:-1]) + '/ffmpeg/bin/ffmpeg' \
                                                                                             '.exe'
        #path_to_ffmpeg_exe = r"D:\GDrive\Documents\2022\BRSAnimPipeline\work\NodeProject\NodeProject\_pipeline_\src\ffmpeg\bin\ffmpeg.exe"
        command = [
            path_to_ffmpeg_exe, '-i', mp3_path,
            '-segment_time', '60',
            '-f', 'segment',
            base_wav_path.replace('.wav','_%03d.wav')]
        subprocess.run(command, check=True)

        audio_files = sorted([wav_dir + os.sep + i for i in os.listdir(wav_dir)])
        #'''
        text_ls = []
        for idx in range(len(audio_files)):
            a_path = audio_files[idx]
            print('Listening.. Track {}/{}| {}% | {}'.format(
                idx, len(audio_files), round(((idx+1)/len(audio_files))*100,2),
                os.path.basename(a_path)))
            #if idx == 6:break

            r = sr.Recognizer()
            audio_file = sr.AudioFile(a_path)
            with audio_file as a_src:
                audio_data = r.record(a_src)
                try:
                    text = r.recognize_google(audio_data)
                except:
                    print('speech_recognition.UnknownValueError\n')
                    text = ''
                text_ls += [text]
                print(text + '\n')

        text_str = '\n'.join(text_ls)
        print(text_str)
        #'''
        if os.path.exists(wav_dir):
            try:shutil.rmtree(wav_dir)
            except:pass

        t = text_str
        t_split = t.split(' ')
        space_count = t.count(' ')
        split_words = 1000
        text_ls = []
        text_ls_idx = 0
        for i in range(len(t_split)):
            w = t_split[i].replace('\n','')
            if text_ls == []:
                text_ls.append([])
            if i % split_words == 0:
                text_ls_idx += 1
                text_ls.append([])
            text_ls[text_ls_idx].append(w)
        text_ls = [i for i in text_ls if i != []]
        text_ls = [' '.join(i) for i in text_ls if i != []]
        print(len(t_split), len(text_ls), json.dumps(text_ls,indent=4))

        #save txt
        with open(txt_path, 'w') as f:
            f.writelines(['{}\n'.format(i) for i in text_ls])
            f.close()

    def cache_transcription_from_podcast_rss(self, count_limit=1):
        df = self.get_all_feed_df()
        df = df.sample(frac=1.0)
        df.reset_index(drop=True, inplace=True)

        mp3_temp_path = cache_dir + os.sep + 'podcast_temp' + '.mp3'

        # each row
        count = 0
        for i in df.index.tolist():
            row = df.loc[i]
            print(row['title'])

            #check exist transcription
            name = row['title'].lower()
            name = ''.join([i for i in name if i.isalpha() or i.isspace() or i.isdigit()]).replace(' ','_')
            txt_path = transcription_dir + os.sep + name + '.txt'
            df.loc[i, 'txt_path'] = txt_path

            #print(txt_path)
            if os.path.exists(txt_path): continue
            if count >= count_limit: continue

            #save mp3
            mp3_url = row['mp3_link']
            with open(mp3_temp_path, 'wb') as f:
                r = requests.get(mp3_url)
                if r.status_code != 200 : continue
                f.write(r.content)
                f.close()

            #extract transcription
            self.transcription(mp3_temp_path, txt_path)
            count += 1

        #export csv
        df.reset_index(drop=True, inplace=True)
        df.to_csv(csv_path, index=False, encoding='utf-8')

podcast_rss = {
    'https://media.rss.com/agoracommunity/feed.xml' : { # agoracommunity
        'title' : ['title'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://allanmckay.libsyn.com/rss' : { # allanmckay
        'title' : ['title'],
        'published' : ['published'],
        'summary' : ['summary'],
        'link' : ['link'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://media.rss.com/thecgbros/feed.xml' : { # thecgbros
        'title' : ['title'],
        'published' : ['published'],
        'summary' : ['summary'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://anchor.fm/s/12548c30/podcast/rss' : { # Directing Animation
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://feeds.libsyn.com/428781/rss' : { # befores & afters
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    },
    'https://ianimate.net/podcast-rss' : { # ianimate
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    },
    'http://www.theanimatedjourney.com/feed/podcast' : { # theanimatedjourney
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    },
    'https://bancroftbros.libsyn.com/rss' : { #bancroftbros
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    },
    'https://schoolofmotion.libsyn.com/rss' : { # schoolofmotion
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    },
    'https://film-book.com/feed/the-animation-podcast' : { # the-animation-podcast
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://feeds.buzzsprout.com/1513429.rss' : { # Creators Society Animation Podcast
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://feeds.buzzsprout.com/2050428.rss' : { # Animated Animators
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    },
    'https://feeds.buzzsprout.com/1782291.rss' : { # The VFX Artists Podcast
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://cglabs.libsyn.com/rss' : { # cglabs
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
        'img_link' : ['image', 'href'],
    },
    'https://www.fxguide.com/category/fxpodcast/feed/' : { # fxpodcast
        'title' : ['title_detail', 'value'],
        'published' : ['published'],
        'summary' : ['summary_detail', 'value'],
        'link' : ['links', 0, 'href'],
        'mp3_link' : ['links', -1, 'href'],
    }
}

if __name__ == '__main__':
    pass
    #pl = plistener(podcast_rss)
    #print(pl.get_feed_df(filter_url='https://anchor.fm/s/c70674cc/podcast/rss'))
    #pl.cache_transcription_from_podcast_rss(count_limit=100)
