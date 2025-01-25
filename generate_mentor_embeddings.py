import openai
import json

openai.api_key = "Add here!"

INPUT_STUDENTS_FILE = "data/mentors.json"
OUTPUT_EMBEDDINGS_FILE = "data/mentor_embeddings.json"
EMBEDDING_MODEL = "text-embedding-ada-002"

def main():
    with open(INPUT_STUDENTS_FILE, "r") as f:
        students_data = json.load(f)

    embeddings_dict = {}

    for record in students_data:
        """
        record structure:
        {
          "student": "Student 1",
          "activities": [...],
          "essays": [...]
        }
        """
        student_name = record.get("student", "Unknown Student")

        text_parts = []
        text_parts.append(f"Student: {student_name}")

        for activity in record.get("activities", []):
            category = activity.get("category", "")
            role = activity.get("role", "")
            organization = activity.get("organization", "")
            description = activity.get("description", "")
            grades = activity.get("grades", [])
            time_commitment = activity.get("time_commitment", "")

            text_parts.append(
                f"Activity - Category: {category}, Role: {role}, Organization: {organization}, "
                f"Description: {description}, Grades: {grades}, Time: {time_commitment}"
            )

        # Include each essay
        for essay in record.get("essays", []):
            title = essay.get("title", "")
            content = essay.get("content", "")
            text_parts.append(f"Essay Title: {title}\n{content}")

        student_text = "\n".join(text_parts)

        response = openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=student_text
        )
        embedding = response.data[0].embedding  # List of floats

        embeddings_dict[student_name] = embedding

        print(f"Generated embedding for {student_name}")

    with open(OUTPUT_EMBEDDINGS_FILE, "w") as out_f:
        json.dump(embeddings_dict, out_f)

    print(f"All student embeddings saved to {OUTPUT_EMBEDDINGS_FILE}.")

if __name__ == "__main__":
    main()
