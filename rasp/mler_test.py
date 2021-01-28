import v_mler


mler = v_mler.Manager()

response = mler.post("WzyWZqBFFaE")
print(response)
print(response.status_code)
print(response.text)
