#1.Create a new text file called myfile.txt and write three lines of text to it.
#2.Read the content of the file and display it on the screen.
#3.Append a new line to the file and display the updated content.
#4.Use with open() to handle file operations properly.
#5.Ensure that the file closes automatically after each operation.

"""with open('myFile.txt', 'w') as file:
    file.write("This is python first program. \nThis is used to handle files.\nAppand Data in it after creation.")
"""
with open('myFile.txt', 'a') as file:
    file.write("\nI append this line through code.")

with open('myFile.txt', 'r') as file:
    print(file.read())