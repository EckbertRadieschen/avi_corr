import json

with open("src/config/grid_config.json", "r") as file:
    grid_config = json.load(file)

count_1 = 0
count_2 = 0
count_3 = 0
greater_3 = 0
greater_5 = 0
greater_10 = 0

for cell, cell_dict in grid_config.items():
    meta_data = cell_dict["meta_data"]
    count = meta_data["route_count"]

    if count > 10: 
        greater_10 += 1
    elif count > 5:
        greater_5 +=1
    elif count > 3:
        greater_3 += 1
    elif count == 3:
        count_3 += 1
    elif count == 2:
        count_2 += 1
    else:
        count_1 += 1
   
print(f"Count 1: {count_1}")
print(f"Count 2: {count_2}")
print(f"Count 3: {count_3}")
print(f"Count 4-5: {greater_3}")
print(f"Count 6-10: {greater_5}")
print(f"Count 11+: {greater_10}")
