from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

def form_details(form):
    details_of_form = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get")
    inputs = []

    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({
            "type": input_type, 
            "name" : input_name,
            "value" : input_value,
        })
        
    details_of_form['action'] = action
    details_of_form['method'] = method
    details_of_form['inputs'] = inputs
    return details_of_form

def vulnerable(response):
    errors = {"quoted string not properly terminated", 
              "unclosed quotation mark after the charachter string",
              "you have an error in you SQL syntax" 
             }
    for error in errors:
        if error in response.content.decode().lower():
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/sql_injection_scan', methods=['POST'])
# def sql_injection_scan():
#     url = request.form['url']
#     forms = get_forms(url)
#     results = []

#     for form in forms:
#         details = form_details(form)
#         for i in "\"'":
#             data = {}
#             for input_tag in details["inputs"]:
#                 if input_tag["type"] == "hidden" or input_tag["value"]:
#                     data[input_tag['name']] = input_tag["value"] + i
#                 elif input_tag["type"] != "submit":
#                     data[input_tag['name']] = f"test{i}"
        
#             if details["method"] == "post":
#                 res = s.post(url, data=data)
#             elif details["method"] == "get":
#                 res = s.get(url, params=data)
#             if vulnerable(res):
#                 results.append("SQL injection attack vulnerability found in form: " + str(details))
#             else:
#                 results.append("No SQL injection attack vulnerability detected")

#     return render_template('results.html', results=results)

# @app.route('/sql_injection_scan', methods=['POST'])
# def sql_injection_scan():
#     url = request.form['url']
#     forms = get_forms(url)
#     results = []

#     for form in forms:
#         details = form_details(form)
#         for i in "\"'":
#             data = {}
#             for input_tag in details["inputs"]:
#                 if input_tag["type"] == "hidden" or input_tag["value"]:
#                     data[input_tag['name']] = input_tag["value"] + i
#                 elif input_tag["type"] != "submit":
#                     data[input_tag['name']] = f"test{i}"
        
#             if details["method"] == "post":
#                 res = s.post(url, data=data)
#             elif details["method"] == "get":
#                 res = s.get(url, params=data)
#             if vulnerable(res):
#                 results.append({
#                     "message": f"SQL injection attack vulnerability found in form: {details}",
#                     "vulnerable": True
#                 })
#             else:
#                 results.append({
#                     "message": "No SQL injection attack vulnerability detected",
#                     "vulnerable": False
#                 })

#     return render_template('results.html', results=results)

@app.route('/sql_injection_scan', methods=['POST'])
def sql_injection_scan():
    url = request.form['url']
    forms = get_forms(url)
    results = []

    # Display the number of forms detected on the website
    results.append(f"Detected {len(forms)} forms on {url}")

    for form in forms:
        details = form_details(form)
        form_result = {
            "message": "No SQL injection attack vulnerability detected",
            "vulnerable": False
        }
        for i in "\"'":
            data = {}
            for input_tag in details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    data[input_tag['name']] = input_tag["value"] + i
                elif input_tag["type"] != "submit":
                    data[input_tag['name']] = f"test{i}"
        
            if details["method"] == "post":
                res = s.post(url, data=data)
            elif details["method"] == "get":
                res = s.get(url, params=data)
            if vulnerable(res):
                form_result["message"] = f"SQL injection attack vulnerability found in form: {details}"
                form_result["vulnerable"] = True
                break  # Break the loop if vulnerability is detected
        
        results.append(form_result)
    

    return render_template('results.html', results=results)



if __name__ == "__main__":
    app.run(debug=True)


'''
https://www.redberyltech.com/#/
https://vtop.vit.ac.in/vtop/login
https://www.amazon.com
https://mail.google.com


'''