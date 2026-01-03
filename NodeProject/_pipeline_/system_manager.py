# -*- coding: utf-8 -*-
import json,os,pprint,sys,time,shutil
import datetime as dt
from typing import Any, Callable, Dict, Generator, List, Optional, Union

"""
Init
"""
base_path = os.path.dirname(os.path.abspath(__file__))
src_path = base_path+'/src'
site_package_path = base_path+'/src'+'/site-packages'

#Environment
if not os.name == 'nt': #Linux
    pass
else:
	if not base_path in sys.path:
		sys.path.insert(0, base_path)
	if not src_path in sys.path:
		sys.path.insert(0, src_path)
	if not site_package_path in sys.path:
		sys.path.insert(0, site_package_path)

# Module
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
from src.gSheet import gSheet
gSheet.sheetName = 'Node Project Integration'
from src.notionDatabase import notionDatabase as ntdb
from src.maReader import maReader

# Path
prev_dir = os.sep.join(base_path.split(os.sep)[:-1])
rec_dir = prev_dir + '/production_rec'
notiondb_dir = rec_dir + '/notionDatabase'

"""
Func
"""

def workspaceSetup(*_):
    path = os.sep.join(base_path.split(os.sep)[:-1]) #\project name
    workspaceJ = json.load(open(base_path + '/workspace.json', 'r'))
    for data in workspaceJ:
        name = data['name']
        makePath = path+'/{}'.format(name)
        if not os.path.isdir(makePath):
            os.makedirs(makePath)
            print('Create Dir {}'.format(makePath))

def versionBackup(extension, dirPath, dateFormat='%Y%m%d_%H%M%S'):
    if not '.' in extension:
        print('Skip backup version because [{}]'.format(extension))
        return None
    if not os.path.exists(dirPath):
        print('Skip backup version because path [{}]'.format(dirPath))
        return None
    for root, dirs, files in os.walk(dirPath, topdown=False):
        for name in files:
            filePath = os.path.join(root, name)
            if 'version' in filePath:
                continue
            if extension in filePath and not '.ini' in filePath:
                versionDir = root + '/version'
                mtime = os.stat(filePath).st_mtime
                dateStr = dt.datetime.fromtimestamp(mtime).strftime(dateFormat)
                new_fileName = name.replace(extension,'') + '_' + dateStr + extension
                new_filePath = root + os.sep + 'version' + os.sep + new_fileName
                if not os.path.exists(versionDir):
                    os.mkdir(versionDir)
                # print(maFilePath)
                if not os.path.exists(new_filePath) and not dateStr in name:
                    print('Backup {}'.format(new_filePath))
                    shutil.copyfile(filePath, new_filePath)

def load_worksheet(sheet, dir_path):
    data = gSheet.getAllDataS(sheet)
    save_path = dir_path + os.sep + sheet + '.json'
    json.dump(data, open(save_path, 'w'), indent=4)
    print('Load worksheet {} - {}'.format(gSheet.sheetName,sheet))

class integration:
    def init_notion_db(*_):
        load_worksheet('nt_database', rec_dir)
        db_path = rec_dir + '/nt_database.json'
        with open(db_path) as db_f:
            db_j = json.load(db_f)

        with open(ntdb.config_path) as r_config_f:
            r_config_j = json.load(r_config_f)
            r_config_j['database'] = db_j
        with open(ntdb.config_path, 'w') as w_config_f:
            json.dump(r_config_j, w_config_f,indent=4)

        ntdb.database = r_config_j['database']

    def load_notion_db(*_):
        if not os.path.exists(notiondb_dir):
            os.makedirs(notiondb_dir)
        ntdb.loadNotionDatabase(notiondb_dir)

    def notion_sheet(*_):
        prev_path = os.sep.join(base_path.split(os.sep)[:-1]).replace('\\','/')
        nt_csv_dir = prev_path + '/production_rec/notionDatabase/csv'
        csv_path_list = [nt_csv_dir + '/' + i for i in os.listdir(nt_csv_dir) if '.csv' in i]
        #print(csv_path_list)
        for csv_path in csv_path_list:
            sheet_dest_name = 'nt_{}'.format(csv_path.split('/')[-1].split('.')[0])
            print('upload destination sheet', sheet_dest_name)
            try:
                gSheet.updateFromCSV(csv_path, sheet_dest_name)
            except:
                print('can\'t upload dataframe to sheet {}'.format(sheet_dest_name))

class data:
    history_dir_name = '_history'

    def create_history(*_):
        for root, dirs, files in os.walk(rec_dir, topdown=False):
            for name in files:
                ext = '.csv'
                if not ext in name:
                    continue
                if data.history_dir_name in root:
                    continue
                file_path = os.path.join(root, name)

                hist_dir_path = os.path.join(root, data.history_dir_name)
                if not os.path.exists(hist_dir_path):
                    os.mkdir(hist_dir_path)

                mtime = os.stat(file_path).st_mtime
                mtime_hour = dt.datetime.fromtimestamp(mtime).hour
                mtime_srtftime = dt.datetime.fromtimestamp(mtime).strftime('%Y%m%d_00')
                if mtime_hour > 12:
                    mtime_srtftime = dt.datetime.fromtimestamp(mtime).strftime('%Y%m%d_01')

                hist_file_path = os.path.join(
                    hist_dir_path, name.replace(ext, '_{}{}'.format(mtime_srtftime, ext)))

                print(os.system('cls||clear'))
                print('create history  ', hist_file_path.split(os.sep)[-1])
                shutil.copyfile(file_path, hist_file_path)

    def clear_past_history(*_):
        for root, dirs, files in os.walk(rec_dir, topdown=False):
            for name in files:
                ext = '.csv'
                if not ext in name:
                    continue
                if data.history_dir_name in root:
                    continue
                file_path = os.path.join(root, name)

                hist_dir_path = os.path.join(root, data.history_dir_name)
                name_no_ext = name.replace(ext,'')

                hist_file_list = sorted([ i for i in os.listdir(hist_dir_path) if name_no_ext in i ])

                file_limit = 5
                if len(hist_file_list) > file_limit:
                    del_file_list = hist_file_list[:-file_limit]
                    keep_file_list = hist_file_list[-file_limit:]
                    #print(del_file_list , keep_file_list)
                    del_path_list = [ os.path.join(hist_dir_path, i) for i in del_file_list ]
                    for i in del_path_list:
                        del_file = del_file_list[del_path_list.index(i)]
                        print('remove off-limit[{}] history files'.format(file_limit), del_file)
                        os.remove(i)

    @staticmethod
    def get_history_path_list(file_path):
        ext = '.csv'
        file_path = file_path.replace('/',os.sep)
        name = os.path.basename(file_path)
        name_no_ext = name.replace(ext,'')
        file_dir = os.path.dirname(file_path)
        hist_dir_path = file_dir + os.sep + data.history_dir_name
        hist_file_list = sorted([ i for i in os.listdir(hist_dir_path) if name_no_ext in i ])
        hist_path_list = [os.path.join(hist_dir_path, i) for i in hist_file_list]
        return hist_path_list

class error:
    file_path = rec_dir + '/main_traceback.csv'

    @staticmethod
    def record(text):
        try:
            data = {
                'date_time': dt.datetime.now().strftime('%m-%d-%Y %H:%M:%S'),
                'traceback' : str(text)
            }
            error.file_path = rec_dir + '/main_traceback.csv'

            df = pd.DataFrame()
            if os.path.exists(error.file_path):
                df = pd.read_csv(error.file_path)
            df = df.append(pd.DataFrame.from_records([data]))
            df.reset_index(inplace=True, drop=True)
            df.to_csv(error.file_path, index=False)
        except:
            pass

    @staticmethod
    def get_nortify(clear_after = True):
        if os.path.exists(error.file_path):
            df = pd.read_csv(error.file_path)
            df.drop_duplicates(['traceback'], inplace=True)
            rec = []
            for i in df.index.tolist():
                row = df.loc[i]
                rec.append(row.to_dict())
            if clear_after:
                os.remove(error.file_path)
            return rec
        else:
            return []

from openai import OpenAI, OpenAIError
class chatgpt_client:
    """
    Lightweight wrapper around the modern OpenAI Python client for chat completions.
    - Uses environment variable OPENAI_API_KEY by default.
    - Uses client.chat.completions.create(...) (structured Chat Completions object).
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: str = "gpt-4o-mini",
            client_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        api_key: explicit API key or None to read from OPENAI_API_KEY
        model: default model id to use
        client_kwargs: any other kwargs to pass to OpenAI(...) constructor (e.g. base_url, timeout)
        """
        client_kwargs = client_kwargs.copy() if client_kwargs else {}
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if resolved_key:
            # pass api_key into the client constructor if provided
            client_kwargs.setdefault("api_key", resolved_key)
        self.client = OpenAI(**client_kwargs)
        self.model = model

    def _build_payload(
            self,
            messages: List[Dict[str, str]],
            *,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
            top_p: Optional[float] = None,
            n: Optional[int] = None,
            presence_penalty: Optional[float] = None,
            frequency_penalty: Optional[float] = None,
            functions: Optional[List[Dict[str, Any]]] = None,
            function_call: Optional[Union[str, Dict[str, Any]]] = None,
            stop: Optional[Union[str, List[str]]] = None,
            **extra,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if n is not None:
            payload["n"] = n
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if functions is not None:
            payload["functions"] = functions
        if function_call is not None:
            payload["function_call"] = function_call
        if stop is not None:
            payload["stop"] = stop
        payload.update(extra)
        return payload

    def chat(
            self,
            messages: List[Dict[str, str]],
            *,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
            stream: bool = False,
            chunk_callback: Optional[Callable[[str], None]] = None,
            retry: int = 1,
            retry_backoff: float = 1.0,
            **kwargs,
    ) -> Union[str, Dict[str, Any], Generator[str, None, None]]:
        """
        Send messages to the Chat Completions API.

        messages: list of {"role": "system|user|assistant", "content": "..."}
        stream: if True, returns a generator yielding text chunks as they're received.
                If chunk_callback is provided, it's called for every chunk as well.
        retry: number of attempts (>=1)
        retry_backoff: seconds to wait between retries (multiplied each retry attempt)

        Returns:
          - If stream=False: returns the assistant text (str) by default. If you need full response object, pass raw=True as a kwarg.
          - If stream=True: returns a generator that yields text chunks (strings).
        """
        attempts = 0
        last_exc = None
        raw = kwargs.pop("raw", False)

        while attempts < retry:
            try:
                payload = self._build_payload(messages, temperature=temperature, max_tokens=max_tokens,
                                              **kwargs)
                if stream:
                    # streaming generator
                    response_iter = self.client.chat.completions.stream(**payload)

                    def _generator() -> Generator[str, None, None]:
                        collected = ""
                        for chunk in response_iter:
                            # The structured streaming chunk shape may vary by SDK version:
                            # Some chunks include {'choices':[{'delta':{'content': '...'}}], ...}
                            # Fall back defensively.
                            try:
                                choices = getattr(chunk, "choices", None) or chunk.get("choices",
                                                                                       None)  # type: ignore
                            except Exception:
                                choices = None
                            delta_text = ""
                            if choices:
                                # iterate all choices and collect content fragments
                                for c in choices:
                                    delta = c.get("delta") if isinstance(c, dict) else getattr(c, "delta", None)
                                    if delta:
                                        part = delta.get("content") if isinstance(delta, dict) else getattr(
                                            delta, "content", None)
                                        if part:
                                            delta_text += part
                            # fallback: some SDKs stream plain text chunks
                            if not delta_text:
                                # try direct text field
                                dt = getattr(chunk, "text", None) or (
                                    chunk.get("text") if isinstance(chunk, dict) else None)
                                if dt:
                                    delta_text = dt
                            if delta_text:
                                collected += delta_text
                                if chunk_callback:
                                    try:
                                        chunk_callback(delta_text)
                                    except Exception:
                                        pass
                                yield delta_text
                        # generator completes

                    return _generator()
                else:
                    resp = self.client.chat.completions.create(**payload)
                    if raw:
                        return resp
                    # extract text from structured response
                    try:
                        # modern structured object: resp.choices[0].message["content"]
                        first_choice = resp.choices[0]
                        message = first_choice.message if hasattr(first_choice, "message") else (
                            first_choice.get("message") if isinstance(first_choice, dict) else None)
                        content = message.get("content") if isinstance(message, dict) else getattr(message,
                                                                                                   "get",
                                                                                                   lambda k,
                                                                                                          d=None: None)(
                            "content") if message is not None else None
                        if content is None:
                            # alternative: some SDKs put text in resp.choices[0].delta or resp.choices[0].text
                            content = getattr(first_choice, "text", None) or (
                                first_choice.get("text") if isinstance(first_choice, dict) else None)
                        return content if content is not None else resp
                    except Exception:
                        return resp
            except OpenAIError as e:
                last_exc = e
                attempts += 1
                if attempts >= retry:
                    raise
                time.sleep(retry_backoff * attempts)
            except Exception as e:
                # non-OpenAI exceptions: break or retry depending on attempts
                last_exc = e
                attempts += 1
                if attempts >= retry:
                    raise
                time.sleep(retry_backoff * attempts)

        # if all retries failed, raise last exception
        if last_exc:
            raise last_exc

    # convenience helpers
    def ask(self, text: str, *, system: Optional[str] = None, **kwargs) -> Union[str, Dict[str, Any]]:
        """
        One-shot user prompt convenience wrapper.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": text})
        return self.chat(messages, **kwargs)

#--------------------------------------------------------

class dinoponique: # home & farm iot system
    @staticmethod
    def run_ezviz_rtsp_image_capture(ssid):
        if ssid != 'nang':
            print('Mismatching SSID to run rtsp capture : {}'.format([ssid]))
            time.sleep(2)
            return
        import subprocess
        print('Run rtsp_ezviz_image_capture..')
        app_dir = src_path + os.sep + 'ezviz_recorder'
        python_path = src_path + os.sep + r"python-3.7.0-embed-amd64\python.exe" if os.name == 'nt' else 'python3'
        python_path = os.path.abspath(python_path) if os.name == 'nt' else python_path
        run_path = app_dir + os.sep + 'ezviz_rtsp_image_capture.py'
        run_path = os.path.abspath(run_path)
        if python_path != python_path.replace(' ', '') or run_path != run_path.replace(' ', ''):
            print('path warning!... \nthe path has space and there will be unsuccessful run')
            time.sleep(5)
        if os.name == 'nt':  # For Windows
            subprocess.Popen(['start', 'cmd', '/K', python_path, run_path], shell=True)  # Open a Command Prompt window and keep it open
        elif os.name == 'posix':  # For Unix-based systems (Linux, macOS)
            #subprocess.call(['lxterminal', '-t', 'EZVIZ INTERVAL CAP', '-e', '{} {}'.format(python_path, run_path)])
            subprocess.Popen(['x-terminal-emulator', '-T', 'EZVIZ INTERVAL CAP', '-e', python_path, run_path])

if __name__ == '__main__':
    #base_path = os.sep.join(base_path.split(os.sep)[:-1])
    #workspaceSetup()
    #versionBackup('.ma', base_path)
    #integration.init_notion_db()
    #integration.load_notion_db()
    #integration.notion_sheet()
    #data.create_history()
    #data.clear_past_history()
    #print(data.get_history_path_list(r"D:\GDrive\Documents\2022\BRSAnimPipeline\work\NodeProject\NodeProject\production_rec\notionDatabase\csv\project.csv"))
    pass
