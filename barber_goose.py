import tkinter as tk
import customtkinter
import subprocess
import queue
import os
import requests
import shutil
import threading
from tkinter import filedialog

import os
import shutil

def clean_vagrant_folder():
    try:
        root_folder_path = file_path_entry.get().strip()

        if not root_folder_path:
            info_text.insert(tk.END, "Укажите путь к папке для очистки.\n")
            return

        if not os.path.exists(root_folder_path):
            info_text.insert(tk.END, f"Папка {root_folder_path} не найдена.\n")
            return

        for filename in os.listdir(root_folder_path):
            file_path = os.path.join(root_folder_path, filename)
            if os.path.isdir(file_path) and filename != "scripts":
                shutil.rmtree(file_path)
            elif os.path.isfile(file_path) and filename != "Vagrantfile":
                os.unlink(file_path)

        info_text.insert(tk.END, f"Папка {root_folder_path} очищена, за исключением папки scripts и Vagrantfile.\n")
        info_text.see(tk.END)
    except Exception as e:
        info_text.insert(tk.END, f"Ошибка при очистке папки {root_folder_path}: {e}\n") # type: ignore


def delete_vagrant_machines():
    try:
        root_folder_path = file_path_entry.get().strip()
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(["vagrant", "halt", "--force"], cwd=root_folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
        return_code = proc.wait()
        if return_code != 0:
            error_message = proc.stderr.read() # type: ignore
            info_text.insert(tk.END, f"Ошибка при остановке машин Vagrant: {error_message}\n")
        else:
            info_text.insert(tk.END, "Машины Vagrant успешно остановлены.\n")
    except Exception as e:
        info_text.insert(tk.END, f"Ошибка при удалении машин Vagrant или очистке папки {file_path_entry}: {e}\n")

def validate_num_copies(P):
    return P.isdigit()

def generate_vagrantfile():
    num_copies = num_copies_entry.get().strip()
    selected_value = machine_name_var.get()

    if selected_value == "Other":
        machine_name = machine_name_entry.get().strip()
    else:
        machine_name = selected_value

    try:
        num_copies = int(num_copies)
    except ValueError:
        info_text.insert(tk.END, "Введите корректное количество копий.\n")
        return

    file_path = file_path_entry.get().strip()

    if not file_path:
        info_text.insert(tk.END, "Укажите путь сохранения Vagrantfile.\n")
        return

    vagrant_file_path = os.path.join(file_path, "Vagrantfile")

    with open(vagrant_file_path, 'w') as file:
        file.write('Vagrant.configure("2") do |config|\n')
        file.write('  config.vm.box = "wvwin10-full"\n')
        file.write('  config.vm.communicator = "winrm"\n')
        file.write('  config.vm.box_check_update = false\n')
        file.write('  config.vm.usable_port_range = 8000..8999\n')
        file.write('  config.vm.synced_folder ".", "/vagrant", disabled: true\n\n')

        machine_names = [f'"{machine_name}-{i:02d}"' for i in range(1, num_copies + 1)]
        machine_names_str = ',\n'.join(machine_names)


        file.write(f' [{machine_names_str}].each do |i|\n')
        file.write('   config.vm.define "#{i}" do |pcn|\n')
        file.write('    pcn.vm.provision "file", source: "scripts/#{i}.txt", destination: "C:\\\\Users\\\\vagrant\\\\Downloads\\\\#{i}.ps1"\n')
        file.write('    pcn.vm.provision "file", source: "scripts/ZauMbuPb2.exe", destination: "C:\\\\Users\\\\vagrant\\\\Downloads\\\\ZauMbuPb2.exe"\n')
        file.write('    pcn.vm.provision "shell", inline: "Start-Process \'C:/Users/vagrant/Downloads/ZauMbuPb2.exe\'"\n')
        file.write('   end\n')

        file.write('  end\n\n')
        file.write('  config.vm.provider "vmware_desktop" do |vd|\n')
        file.write('    vd.vmx["memsize"] = "4096"\n')
        file.write('    vd.vmx["numvcpus"] = "2"\n')
        file.write('    vd.vmx["cpuid.coresPerSocket"] = "2"\n')
        file.write('    vd.gui = true\n')
        file.write('    vd.vmx["mks.enable3d"] = "TRUE"\n')
        file.write('    vd.vmx["svga.graphicsMemoryKB"] = "1048576"\n')
        file.write('  end\n')
        file.write('end\n')

    def create_vagrantfile():
        try:
            scripts_folder_path = os.path.join(file_path, "scripts")
            os.makedirs(scripts_folder_path, exist_ok=True)

            url = "https://github.com/AndreiBeirit/zaumbupb/raw/main/ZauMbuPb2.exe"

            try:
                script_content = '''function GenerateRandomSuffix {
    $characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $suffix = -join ((0..5) | ForEach-Object { $characters[(Get-Random -Maximum $characters.Length)] })
    return $suffix
}
$scriptFiles = Get-ChildItem "C:/Users/vagrant/Downloads/" -Filter *.ps1
if ($scriptFiles.Count -gt 0) {
    $firstTwoLetters = $scriptFiles[0].BaseName.Substring(0, 2)
} else {
    $firstTwoLetters = -join ((0..1) | ForEach-Object { $characters[(Get-Random -Maximum $characters.Length)] })
}
$newDeviceName = "PC-" + $firstTwoLetters + (GenerateRandomSuffix)
Rename-Computer -NewName $newDeviceName -Force -Restart
'''
                for i in range(1, num_copies + 1):
                    script_file_path = os.path.join(scripts_folder_path, f"{machine_name}-{i:02d}.txt")
                    with open(script_file_path, 'w') as script_file:
                        script_file.write(script_content)
                    info_text.insert(tk.END, f"Создан файл {script_file_path} для машины {machine_name}-{i:02d}.\n")
                    info_text.see(tk.END)
            except Exception as e:
                info_text.insert(tk.END, f"Ошибка при создании скриптов: {e}\n")
            info_text.insert(tk.END, "Ждём загрузки автоматизационного ПО.\n")

            response = requests.get(url)
            if response.status_code == 200:
                file_path_exe = os.path.join(scripts_folder_path, "ZauMbuPb2.exe")
                with open(file_path_exe, 'wb') as file:
                    file.write(response.content)

                info_text.insert(tk.END, f"Создана папка {scripts_folder_path} для скриптов.\n")
                info_text.insert(tk.END, "Файл ZauMbuPb2.exe успешно загружен и сохранен в папку scripts.\n")
            else:
                info_text.insert(tk.END, "Не удалось загрузить файл ZauMbuPb2.exe. Проверьте ссылку или интернет-соединение.\n")

            info_text.insert(tk.END, f"Создан файл {file_path}/Vagrantfile с {num_copies} копиями машины {machine_name}.\n")
            info_text.see(tk.END)

        except Exception as e:
            info_text.insert(tk.END, f"Ошибка: {e}\n")

    threading.Thread(target=create_vagrantfile).start()

log_queue = queue.Queue()

def deploy_vagrant():
    file_path = file_path_entry.get().strip()
    if not file_path:
        info_text.insert(tk.END, "Не указан путь к Vagrantfile.\n")
        return

    vagrant_file_path = os.path.join(file_path, "Vagrantfile")
    if not os.path.exists(vagrant_file_path):
        info_text.insert(tk.END, f"Файл {vagrant_file_path} не найден.\n")
        return

    try:
        info_text.insert(tk.END, "Запускаем deploy!\n")
        def run_vagrant():
            try:
                root_folder_path = file_path_entry.get().strip()
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                process = subprocess.Popen(["vagrant", "up"], cwd=root_folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
                
                for line in iter(process.stdout.readline, ''): # type: ignore
                    log_queue.put(line)
                
                process.stdout.close() # type: ignore
                return_code = process.wait()

                if return_code != 0:
                    log_queue.put(f"Команда 'deploy' завершилась с ошибкой. Код ошибки: {return_code}\n")
                else:
                    log_queue.put("Команда 'deploy' выполнена успешно.\n")
            except Exception as e:
                log_queue.put(f"Ошибка выполнения команды 'deploy': {e}\n")
        
        log_queue = queue.Queue()
        threading.Thread(target=run_vagrant).start()

        def update_logs():
            while True:
                try:
                    log = log_queue.get_nowait()
                    info_text.insert(tk.END, log)
                    info_text.see(tk.END)
                except queue.Empty:
                    break
            root.after(100, update_logs)
        
        update_logs()

    except Exception as e:
        info_text.insert(tk.END, f"Ошибка выполнения команды 'vagrant up': {e}\n")

def clear_folder():
    file_path = file_path_entry.get().strip()
    if not file_path:
        info_text.insert(tk.END, "Не указан путь к Vagrantfile.\n")
        return
    
    root_folder_path = file_path_entry.get().strip()
    files_in_folder = os.listdir(root_folder_path)
    if not files_in_folder:
        info_text.insert(tk.END, f"Папка {root_folder_path} уже пуста.\n")
        info_text.see(tk.END)
        return

    def clear():
        try:
            info_text.insert(tk.END, "Выключаем машинки...\n")
            delete_vagrant_machines()
            info_text.insert(tk.END, "Машинки выключены, ждём остановки сервисов и чистим папку...\n")
            root.after(10000, clean_vagrant_folder)
        except Exception as e:
            info_text.insert(tk.END, f"Ошибка при очистке папки {file_path_entry} или выключении машин Vagrant: {e}\n")
        else:
            log_queue.put("Очистка завершена!\n")

    threading.Thread(target=clear).start()

def select_vagrantfile_path():
    chosen_path = filedialog.askdirectory()
    if chosen_path:
        file_path_entry.delete(0, tk.END)
        file_path_entry.insert(tk.END, chosen_path)

        vagrant_file_path = os.path.join(chosen_path, "Vagrantfile")
        if os.path.exists(vagrant_file_path):
            show_vagrantfile_info(vagrant_file_path)

def show_vagrantfile_info(vagrant_file_path):
    try:
        with open(vagrant_file_path, 'r') as file:
            content = file.read()
            start = content.find('[')
            end = content.find(']', start) + 1 if start != -1 else -1

            if start != -1 and end != -1:
                machines = content[start:end]
                machine_names = machines.replace("'", "").split(", ")
                
                info_text.delete(1.0, tk.END)
                info_text.insert(tk.END, "Список машинок в конфиге:\n")
                for name in machine_names:
                    info_text.insert(tk.END, f"{name}\n")
            else:
                info_text.insert(tk.END, "Не найден список наименований профилей в файле.\n")
    except FileNotFoundError:
        info_text.insert(tk.END, f"Файл {vagrant_file_path} не найден.\n")
    except Exception as e:
        info_text.insert(tk.END, f"Ошибка при чтении файла {vagrant_file_path}: {e}\n")


def on_option_selected(*args):
    selected_value = machine_name_var.get()
    if selected_value == "Other":
        machine_name_entry.configure(state=tk.NORMAL)
        machine_name_entry.delete(0, tk.END)
    else:
        machine_name_entry.configure(state=tk.DISABLED)
        machine_name_entry.delete(0, tk.END)
        machine_name_entry.insert(0, selected_value)

def stop_ruby_interpreter():
    try:
        root_folder_path = file_path_entry.get().strip()
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process_list = subprocess.run(["tasklist", "/fi", 'imagename eq ruby.exe', "/fo", "csv"], cwd=root_folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
        processes = process_list.stdout.splitlines()
        if len(processes) > 1:
            for process in processes[1:]:
                pid = process.split(",")[1].strip('"')
                subprocess.run(["taskkill", "/f", "/pid", pid], cwd=root_folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
            info_text.insert(tk.END, "Процесс развертки остановлен.\n")
        else:
            info_text.insert(tk.END, "Процесс развертки не найден.\n")
    except subprocess.CalledProcessError as e:
        info_text.insert(tk.END, f"Ошибка при остановке процессов Ruby interpreter: {e}\n")


root = customtkinter.CTk()
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
root.geometry("600x400")
root.resizable(False, False)
root.title("Барбершоп для гусей_v1.7")

file_path_frame = customtkinter.CTkFrame(root)
file_path_frame.pack(pady=10)
file_path_label = customtkinter.CTkLabel(file_path_frame, text="Выбрать путь к Vagrantfile:")
file_path_label.pack(side=tk.LEFT, padx=10, pady=5)
file_path_entry = customtkinter.CTkEntry(file_path_frame, width=200)
file_path_entry.pack(side=tk.LEFT, padx=10, pady=5)
browse_button = customtkinter.CTkButton(file_path_frame, text="Browse", command=select_vagrantfile_path)
browse_button.pack(side=tk.LEFT, padx=10, pady=5)

input_frame = customtkinter.CTkFrame(root)
input_frame.pack(pady=20)

machine_name_label = customtkinter.CTkLabel(input_frame, text="Как назвать ВМ?")
machine_name_label.grid(row=0, column=0, padx=10, pady=5)

machine_name_var = customtkinter.StringVar(value="US-Chat")
machine_name_var.trace_add("write", on_option_selected)
machine_name = customtkinter.CTkOptionMenu(input_frame,
                                           values=["EU-Chat", "US-Chat", "Other"],
                                           variable=machine_name_var)
machine_name.grid(row=0, column=1, padx=10, pady=5)
machine_name_entry = customtkinter.CTkEntry(input_frame, state=tk.DISABLED)
machine_name_entry.grid(row=0, column=2, padx=10, pady=5)

num_copies_label = customtkinter.CTkLabel(input_frame, text="Сколько копий?")
num_copies_label.grid(row=1, column=0, padx=10, pady=5)

start_button = customtkinter.CTkButton(input_frame, text="Собрать конфиг", command=generate_vagrantfile)
start_button.grid(row=1, column=2, padx=10, pady=5)

validate_num_copies_cmd = root.register(validate_num_copies)
num_copies_entry = customtkinter.CTkEntry(input_frame, validate="key", validatecommand=(validate_num_copies_cmd, "%P"))
num_copies_entry.grid(row=1, column=1, padx=10, pady=5)

button_frame = customtkinter.CTkFrame(root)
button_frame.pack()

deploy_button = customtkinter.CTkButton(button_frame, text="Развернуть", command=deploy_vagrant)
deploy_button.pack(side=tk.LEFT, padx=10, pady=10)

stop_button = customtkinter.CTkButton(button_frame, text="Остановить", command=stop_ruby_interpreter)
stop_button.pack(side=tk.LEFT, padx=10, pady=10)

clear_button = customtkinter.CTkButton(button_frame, text="Уничтожить/Почистить", command=clear_folder)
clear_button.pack(side=tk.LEFT, padx=10, pady=10)

info_text = customtkinter.CTkTextbox(root, height=300, width=550)
info_text.pack(pady=20)

root.mainloop()