import pandas as pd


def check_employee(employee_id, file_path):
    # read file
    df = pd.read_excel(file_path)

    # check employee_id
    if employee_id in df['Employee ID'].values:
        print(f"Employee {employee_id} is already registered.")
        return True
    else:
        return


def write_to_excel(employee_id, first_name, last_name, date_of_birth, image_url, file_path):
    try:
        try:
            existing_data = pd.read_excel(file_path)
            df = pd.DataFrame(existing_data)
        except FileNotFoundError:
            df = pd.DataFrame()

        # Create a new dataset
        new_data = {
            'Employee ID': [employee_id],
            'First Name': [first_name],
            'Last Name': [last_name],
            'Date of Birth': [date_of_birth],
            'Image URL': [image_url]
        }

        # Adding new data to a DataFrame
        new_df = pd.DataFrame(new_data)

        # Adding new data to an existing DataFrame
        df = df.append(new_df, ignore_index=True)

        # Create or update an Excel file
        df.to_excel(file_path, index=False)

        print("Data added successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


def get_employee_list_with_details(file_path):
    try:
        # read excel_file
        df = pd.read_excel(file_path)

        # return employees list
        employee_list = []

        for index, row in df.iterrows():
            employee = {
                'employee_id': row['Employee ID'],
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'date_of_birth': row['Date of Birth'].date(),
                'image_url': row['Image URL']
            }
            employee_list.append(employee)

        return employee_list

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
