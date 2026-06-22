# Clinic Management System using Tkinter
import tkinter as tk
from tkinter import messagebox

# List to store patient records
patients = []

# ---------------- FUNCTIONS ---------------- #

def add_patient():
    name = entry_name.get()
    age = entry_age.get()
    gender = entry_gender.get()
    symptoms = entry_symptoms.get()

    # Validation
    if name == "" or age == "" or gender == "" or symptoms == "":
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    # Store patient data as dictionary
    patient = {
        "Name": name,
        "Age": age,
        "Gender": gender,
        "Symptoms": symptoms
    }

    patients.append(patient)
    messagebox.showinfo("Success", "Patient added successfully!")

    clear_fields()


def view_patients():
    output.delete("1.0", tk.END)

    if len(patients) == 0:
        output.insert(tk.END, "No patient records found.\n")
        return

    for i, patient in enumerate(patients, start=1):
        record = f"""
Patient {i}
Name: {patient['Name']}
Age: {patient['Age']}
Gender: {patient['Gender']}
Symptoms: {patient['Symptoms']}
---------------------------
"""
        output.insert(tk.END, record)


def search_patient():
    name = entry_name.get()
    output.delete("1.0", tk.END)

    found = False
    for patient in patients:
        if patient["Name"].lower() == name.lower():
            record = f"""
Patient Found:
Name: {patient['Name']}
Age: {patient['Age']}
Gender: {patient['Gender']}
Symptoms: {patient['Symptoms']}
"""
            output.insert(tk.END, record)
            found = True
            break

    if not found:
        output.insert(tk.END, "Patient not found.\n")


def clear_fields():
    entry_name.delete(0, tk.END)
    entry_age.delete(0, tk.END)
    entry_gender.delete(0, tk.END)
    entry_symptoms.delete(0, tk.END)


def delete_patient():
    name = entry_name.get()

    for patient in patients:
        if patient["Name"].lower() == name.lower():
            patients.remove(patient)
            messagebox.showinfo("Deleted", "Patient record deleted!")
            return

    messagebox.showwarning("Error", "Patient not found!")


# ---------------- GUI DESIGN ---------------- #

root = tk.Tk()
root.title("Clinic Management System")
root.geometry("500x500")

# Labels and Entries
tk.Label(root, text="Clinic Management System", font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(root, text="Name").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Age").pack()
entry_age = tk.Entry(root)
entry_age.pack()

tk.Label(root, text="Gender").pack()
entry_gender = tk.Entry(root)
entry_gender.pack()

tk.Label(root, text="Symptoms").pack()
entry_symptoms = tk.Entry(root)
entry_symptoms.pack()

# Buttons
tk.Button(root, text="Add Patient", command=add_patient).pack(pady=5)
tk.Button(root, text="View Patients", command=view_patients).pack(pady=5)
tk.Button(root, text="Search Patient", command=search_patient).pack(pady=5)
tk.Button(root, text="Delete Patient", command=delete_patient).pack(pady=5)
tk.Button(root, text="Clear Fields", command=clear_fields).pack(pady=5)

# Output Area
output = tk.Text(root, height=10, width=50)
output.pack(pady=10)

# Run App
root.mainloop()