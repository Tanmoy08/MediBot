import json
import time
from requests import get, post

class RecognizeCustomForms:
    def __init__(self):
        self.endpoint = r"https://preranafrresource.cognitiveservices.azure.com/"
        self.apim_key = "3fe235a8d6b445c4b5284017a8e64f8c"
        self.model_id = "02a7178f-c2e0-40dc-b43d-66c3fde1e04a"
        #self.source = img_path
        self.post_url = self.endpoint + "/formrecognizer/v2.1-preview.3/custom/models/%s/analyze" % self.model_id
        self.params = {
                        "includeTextDetails": True
                        }
        self.headers = {
                        # Request headers
                        'Content-Type': 'image/png', # Replace with appropriate content type, eg: image/png
                        'Ocp-Apim-Subscription-Key': self.apim_key,
                        }
            
    def recognize_custom_forms(self,data):
        data_bytes = data
        try:
            prediction_result = dict.fromkeys(['status','message','json'])
            resp = post(url = self.post_url, data = data_bytes, headers = self.headers, params = self.params)
            if resp.status_code != 202:
                prediction_result['message'] = json.dumps(resp.json())
                raise Exception("Error occured during post")
            else:
                prediction_result['message'] = json.dumps("POST analyze succeeded")
    
            get_url = resp.headers["operation-location"]    
    
            time.sleep(6)
    
            n_tries = 5
            n_try = 0
            wait_sec = 4
            max_wait_sec = 40
            while n_try < n_tries:
                #print("Num. of tries:",n_try)
                resp_get = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": self.apim_key})
                resp_json = resp_get.json()
                #print("resp json:",resp_json)
                #if resp_get.status_code == 200:
                if resp_json["status"] == "succeeded":
                    #print("Success")
                    prediction_result['status'] = "success"
                    prediction_result['message'] = "Form OCR succeeded."
                    prediction_result['json'] = resp_json
                    #print("inside if ", n_try)
                    #print(resp_json)
                    break
                else:
                    #print(json.dumps(resp_json))
                    #print("number of try:", n_try)
                    prediction_result['status'] = resp_json["modelInfo"]["status"]
                    prediction_result['message'] = json.dumps(resp_json)
                    time.sleep(wait_sec)
                    n_try += 1
                    wait_sec = min(2*wait_sec, max_wait_sec)
                    #print("inside else", n_try)
                    
            return prediction_result
            
    
        except Exception as e:
            prediction_result['status'] = "fail" 
            prediction_result['message'] = prediction_result['message'] + str(e)
            return prediction_result
        





