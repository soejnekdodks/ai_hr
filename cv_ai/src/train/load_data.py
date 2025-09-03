import sys
import json


def parse(data: dict):
    output_data = {
        "localityName": data.get("localityName"),
        "birthday": data.get("birthday"),
        "gender": data.get("gender"),
        "salaryMin": data.get("salaryMin"),
        "salaryMax": data.get("salaryMax"),
        "shifts": data.get("shifts", []),
        "positionName": data.get("positionName"),
        "worldskills": data.get("worldskills", []),
        "driveLicenses": data.get("driveLicenses", []),
        "experience": data.get("experience"),
        "professionList": [],
        "educationList": [],
        "education": data.get("education"),
        "hardSkills": data.get("hardSkills", []),
        "softSkills": data.get("softSkills", []),
        "skills": data.get("skills", []),
        "workExperienceList": [],
        "scheduleType": data.get("scheduleType"),
        "salary": data.get("salary"),
        "desirableRelocationRegions": data.get("desirableRelocationRegions", []),
        "languageKnowledge": data.get("languageKnowledge", []),
        "country": [],
        "age": data.get("age"),
    }

    if "professionList" in data:
        for profession in data["professionList"]:
            output_data["professionList"].append(
                {"codeProfessionalSphere": profession.get("codeProfessionalSphere")}
            )

    if "educationList" in data:
        for education in data["educationList"]:
            output_data["educationList"].append(
                {"instituteName": education.get("instituteName")}
            )

    if "workExperienceList" in data:
        for experience in data["workExperienceList"]:
            output_data["workExperienceList"].append(
                {
                    "companyName": experience.get("companyName"),
                    "dateFrom": experience.get("dateFrom"),
                    "dateTo": experience.get("dateTo"),
                    "demands": experience.get("demands"),
                    "jobTitle": experience.get("jobTitle"),
                    "relevant": experience.get("relevant"),
                    "type": experience.get("type"),
                }
            )

    if "country" in data:
        for country in data["country"]:
            output_data["country"].append({"countryName": country.get("countryName")})

    return output_data


def process_json():
    with open("/home/psidjik/code/ai_hr/cv_ai/dataset/cv.json", "r") as in_file:
        with open("/home/psidjik/code/ai_hr/cv_ai/dataset/cv_2.json", "w") as out_file:
            cnt = 0
            size = 0
            a = json.loads(in_file.readline()[8:-2])
            out_file.write(str(parse(a)) + "," + "\n")
            while True:
                if line := json.loads(in_file.readline()[:-2]):
                    out_file.write(str(parse(line)) + "," + "\n")
                    cnt += 1
                    size += sys.getsizeof(line)
                    if cnt % 10000 == 0:
                        print(cnt, size // 1024 // 1024 // 1024)
                else:
                    return


process_json()
