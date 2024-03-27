import math
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from functools import lru_cache
import math
import os
import sys
from jinja2 import Environment, FileSystemLoader

#global variables
piston_density = None
rod_density = None
crankshaft_density = None
camshaft_density = None

#function for grabbing user input for use in math_bits function and write_file function
@lru_cache(maxsize=None)
def user_input():
    bore = int(input("Enter bore diameter in mm: "))
    throw = int(input("Enter throw length in mm: "))
    cr = int(input("Enter compression ratio: "))
    deck_clearance = int(input("Enter clearance of deck in mm: "))
    redline = int(input("Enter redline rpm: "))
    cylinder_number = int(input("Enter number of cylinders must be integerly divisible by number of banks: "))
    bank_number = int(input("Enter number of banks: "))
    cam_lift = int(input("Enter cam lift: "))
    cam_duration = int(input("Enter cam duration: "))
    rod_angle = int(input("Enter rod angle at 90 degrees atdc: "))
    peak_torque_rpm = int(input("Enter rpm at which peak torque will theoretically occur (must be less than redline to be valid): "))
    valves_per_cylinder = int(input("Enter number of valves per cylinder: "))
    exhaust_primary_length = int(input("Enter primary length of exhaust pipe: "))
    firing_order = tuple(map(int, input("Type out the firing order as a comma-separated list. Remember to include all cylinders once and only once, must start with 1: ").split(",")))
    bank_angle = int(input("Enter angle between outer engine banks or angle of bank for inline slant engine: "))
    name_of_engine = input("Input name of engine in simulator: ")

    return (bore, throw, cylinder_number, bank_number, cam_lift, cam_duration, rod_angle, peak_torque_rpm, cr, deck_clearance, redline, valves_per_cylinder, exhaust_primary_length, firing_order, bank_angle, name_of_engine)

#function for changing global vaues based on gui dropdown selections and then destroying appropriate gui window    
def handle_selection(event=None):
    
    global piston_density, rod_density, crankshaft_density, camshaft_density
    
    #grabs values from densities gui
    selected_item_1 = dropdown_1.get()
    selected_item_2 = dropdown_2.get()
    selected_item_3 = dropdown_3.get()
    selected_item_4 = dropdown_4.get()

    #finds numbers inside gotten values by looking for parentheses
    start_index_1 = selected_item_1.find('(')
    end_index_1 = selected_item_1.find(')')
    start_index_2 = selected_item_2.find('(')
    end_index_2 = selected_item_2.find(')')
    start_index_3 = selected_item_3.find('(')
    end_index_3 = selected_item_3.find(')')
    start_index_4 = selected_item_4.find('(')
    end_index_4 = selected_item_4.find(')')

    #extracts out numbers from values
    if start_index_1 != -1 and end_index_1 != -1:
        piston_density = selected_item_1[start_index_1 + 1:end_index_1]

    if start_index_2 != -1 and end_index_2 != -1:
        rod_density = selected_item_2[start_index_2 + 1:end_index_2]

    if start_index_3 != -1 and end_index_3 != -1:
        crankshaft_density = selected_item_3[start_index_3 + 1:end_index_3]

    if start_index_4 != -1 and end_index_4 != -1:
        camshaft_density = selected_item_4[start_index_4 + 1:end_index_4]

    print(piston_density, rod_density, crankshaft_density, camshaft_density)

    #creates list for later use in checking
    var_list = [piston_density, rod_density, crankshaft_density, camshaft_density]

    # Check if all variables have a non-None value using a list comprehension and all()
    all_have_value = all(var is not None for var in var_list)

    # if previous line returns yes then destrot the densities gui window
    if all_have_value:
        densities.destroy()

#performs various math
def math_bits():
    #grabs the return of the user_input function as a tuple
    result_tuple = user_input()
    
    #determines the rod length by performing math on values returned from user_input function
    rod_length_value = result_tuple[1] * (1/(math.cos(result_tuple[6])))

    #dynamically creates a list using variables returned from user_input_function
    wires_list = [
        f'.connect_wire(wires.wire{order}, ({index-1}/{result_tuple[2]}) * cycle)'
        for index, order in enumerate(result_tuple[13], start=1)
    ]
    #re does the list wires_list in a vertical format with single line spacing
    wires = '\n\t\t\t'.join(wires_list)

    #creates an empty list
    ignition_list = []

    #uses a for loop based on variables returned from user_input to append items to the empty list ignition_list
    for i in range(1, result_tuple[2]+1):
        result = f'output wire{i}: ignition_wire();'
        ignition_list.append(result)

    #re does the completed list ignition_list in a vertical format with single line spacing
    ignition = '\n\t'.join(ignition_list)

    #creates an empty list
    angles = []

    #Check if the fourth element in result_tuple is even.
    # If it is, iterate downwards from half of the fourth element minus one to 1, calculating and appending angles based on a formula
    if result_tuple[3] == 1:
        angles[0] = result_tuple[14]
    elif result_tuple[3] % 2 == 0:
        for x in range((result_tuple[3]//2), 0, -1):
            result = -(((result_tuple[14]/2) / (result_tuple[3]/2)) * x)
            angles.append(result)   
    # If the fourth element in result_tuple is not even, execute this block.
    # Iterate downwards from half of the fourth element to 1, calculating and appending angles based on a formula.
    else:
        for x in range(result_tuple[3]//2, 0, -1):
            result = -(((result_tuple[14]/2) / (result_tuple[3]/2)) * x)
            angles.append(result)

    #sums toghether all values from the list angles
    crank_angle = sum(angles)        
    
    #check if the fourth element in result_tuple is odd if it is then append a 0 to the list angles
    if result_tuple[3] % 2 != 0 and result_tuple[3] != 1:
        angles.append(0)

    #adds a list to the list angles this list is the reversed negative invese of the angles list
    if result_tuple[3] > 1:
        new_angles = []
        for angle in reversed(angles):
            new_angles.append(-angle)
        angles.extend(new_angles)

    #creates an empty list
    cam_list = []

    #uses a for loop to dynamically append values to the list cam_list
    for c in range (1, result_tuple[3]+1):
        result = f'output intake_cam_{c}: _intake_cam_{c};\noutput exhaust_cam_{c}: _exhaust_cam_{c};'
        cam_list.append(result)

    #redoes cam_list in a vertical format with double line specing
    cams = '''\n\n\t'''.join(cam_list)

    #creates an empty list
    cam_list_2 = []

    #use a for loop to dynamically append values to the list cam_list_2
    for d in range(1, result_tuple[3]+1):
        result = f'camshaft _intake_cam_{d}(params, lobe_profile: intake_lobe_profile)\ncamshaft _exhaust_cam_{d}(params, lobe_profile: exhaust_lobe_profile)'
        cam_list_2.append(result)
    
    #redoes cam_list_2 in a vertical format with double line spacing
    cams_2 = '\n\n\t'.join(cam_list_2)

    #creates a list of lists where the number of lists is the fourth item in result_tuple
    output_lists = [[] for _ in range(result_tuple[3]+1)]

# Determine the maximum value in the input list divided by integer
    max_value_divided = result_tuple[2] // result_tuple[3]

# Split values into respective output lists based on conditions
    for value in result_tuple[13]:
        if value <= max_value_divided:
            output_lists[0].append(value)
        else:
            if result_tuple[3] == 2:
                for i in range(2, result_tuple[3]+1):
                    if value <= max_value_divided * (i):
                        output_lists[i-1].append(value)
                    else:
                        output_lists[-1].append(value)
            else:
                for i in range(2, result_tuple[3]+1):
                    if value <= max_value_divided * (i):
                        output_lists[i-1].append(value)
                    else:
                        output_lists[-1].append(value)

# Modify subsequent output lists using the star algorithm
    star_points = max(output_lists[0])
    #uses nested for loops to dynamically change values inside the sub lists inside the output_lsits list
    for index, value in enumerate(output_lists):
        if index >= 1:
            for x in value:
                #checks if the current value properly divides into the number of star points if yes then the current value is redone as the number of star points
                if x % star_points == 0:
                    y = value.index(x)
                    value[y] = star_points
                #checks if the current value does not properly divide into the number of star points if yes then the current value is redone as the remainder of the division between the curren value and the number of star points
                else:
                    z = value.index(x)
                    value[z] = x % star_points

    #divides the third value in result_tuple by the fourth value in result_tuple
    cam_num = result_tuple[2]//result_tuple[3]
    
    # creates two seperate empty lists
    intake_cam = []
    exhaust_cam = []

    #uses nested for loops to dynamically add values to the intake_cam list
    for e in range(1, result_tuple[3]+1):
        intake_cam_name = f'_intake_cam_{e}'
        cam_output = f'''{intake_cam_name}
                            .add_lobe(rot360 + intake_lobe_center)'''
        intake_values = output_lists[e-1]
        for j in intake_values:
            if j-1 != 0:
                cam_output += f'\t.add_lobe(rot360 + intake_lobe_center + {j-1} * {720/cam_num} + {angles[e-1]})\n'
        intake_cam.append(cam_output)

    #redoes the intake_cam list in a vertical format with double line spacing
    intake_cam_2 = '\n\n\t'.join(intake_cam)

    #uses nested for loops to dynamically add values to the exhaust_cam list
    for f in range(1, result_tuple[3]+1):
        exhaust_cam_name = f'_exhaust_cam_{f}'
        cam_output = f'{exhaust_cam_name}\n\t.add_lobe(rot360 - exhaust_lobe_center)'
        exhaust_values = output_lists[f-1]
        for j in exhaust_values:
            if j-1 !=0:
                cam_output += f'\t.add_lobe(rot360 - exhaust_lobe_center + {j-1} * {720/cam_num} + {angles[f-1]})\n'
        exhaust_cam.append(cam_output)

    #redoes the exhuat_cam list in a vertical format with double line spacing
    exhaust_cam_2 = '\n\n\t'.join(exhaust_cam)

    #creates a list with an intial starting value
    journal_list = [f'rod_journal rj1(angle: 0.0)']

    #uses a for loop to dynamically add values to the journal_list list
    for g in range(2, result_tuple[2]+1):
        #finds the value inside of the 14th value of result_tuple at a certain index
        firing_order_place = result_tuple[13].index(g-1)
        #calculates the division of two numbers then always rounds up to the nearest integer
        bank_2 = math.ceil(g/cam_num)
        #
        result = f'rod_journal rj{g}(angle: {((firing_order_place/result_tuple[2])*360)-(abs(angles[0]-angles[bank_2-1]))})'
        journal_list.append(result)

    #redoes the journal_list list in a vertical format with double line spacing
    journal = '\n\t'.join(journal_list)
 
    #creates an empty list
    journal_list_2 = []

    #uses a for loop to dynamically add values to the journal_list_2 list
    for f in range(1, result_tuple[2]):
        result = f'.add_rod_journal(rj{f})'
        journal_list_2.append(result)
    
    #redoes the journal_list_2 list in a vertical format with single line spacing
    journal_2 = '\n\t\t'.join(journal_list_2)

    #creates an empty list
    banks = []

    #uses nested for loops to dynamically add values to the banks list
    for i in range(1, result_tuple[3]+1):
        bank_name = f'cylinder_bank b{i}(bank_params, angle: {angles[i-1]} * units.deg)\nb{i}'
        banks.append(bank_name)
        for h in range(1, cam_num+1):
            cylinder = f'\n\t.add_cylinder(\n\t\tpiston: piston(piston_params, blowby: k_28inH2O(0.1)),\n\t\tconnecting_rod: connecting_rod(cr_params),\n\t\trod_journal: rj{h*i},\n\t\tintake: intake_1,\n\t\texhaust_system: exhaust0,\n\t\tignition_wire: wires.wire{h * i}\n\t)'
            banks.append(cylinder)
        
    #redoes the banks list in a vertical format with single line spacing
    banks_list = '\n\t'.join(banks)

    #creates an empty list
    banks_2 = []
    
    #uses a for loop to dynamically add values to the banks_2 list
    for i in range(1, result_tuple[3]+1):
        bank = f'.add_cylinder_bank(b{i})'
        banks_2.append(bank)

    #redoes the banks_2 list in a vertical format with single line spacing
    banks_2_list = '\n\t\t'.join(banks_2)

    #creates an empty lsit
    banks_3 = []

    #uses a for loop to dynamically add values to the banks_3 list
    for i in range(1, result_tuple[3]+1):
        result = f'b{i}.set_cylinder_head (\n\tbmw_m52b28_head(\n\t\tintake_camshaft: camshaft.intake_cam_{i},\n\t\texhaust_camshaft: camshaft.exhaust_cam_{i}\n\t)\n)'
        banks_3.append(result)

    #redoes the banks_3 list in a vertical format with single line spacing
    banks_3_list = '\n\t'.join(banks_3)

    return (rod_length_value, wires, ignition, cams, cams_2, intake_cam_2, exhaust_cam_2, crank_angle, journal, journal_2, banks_list, banks_2_list, banks_3_list)
  
def get_template_path():
    # Get the directory where the executable or script is located
    if getattr(sys, 'frozen', False):  # Check if running as a frozen (compiled) executable
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory if running as a script

    # Construct the template file path relative to the executable's directory
    template_file = 'template.txt'
    template_path = os.path.join(base_dir, template_file)
    return template_path

def fill_template(template_path, output_path, **kwargs):
    # Load the template environment
    env = Environment(loader=FileSystemLoader('.'))

    template = env.get_template(os.path.basename(template_path))

    # Render the template with variables
    rendered_template = template.render(**kwargs)

    # Write the filled template to the selected output file
    temp_output_path = output_path
    with open(temp_output_path, 'w') as f:
        f.write(rendered_template)

    
    try:
        base_name, _ = os.path.splitext(temp_output_path)
        new_output_path = f"{base_name}.{'mr'}"
        os.rename(temp_output_path, new_output_path)
        print(f"File extension changed successfully to {'.mr'}")
    except OSError as e:
        print(f"Error changing file extension: {e}")
        new_output_path = None

def select_output_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    output_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt')])
    return output_path

def generate_variables():
    result_tuple = user_input()
    result_tuple_2 = math_bits()

    variables = []

    variables.append(('bore', f'{result_tuple[0]}'))
    variables.append(('throw', result_tuple[1]))
    variables.append(('cyl_number', result_tuple[2]))
    variables.append(('bank_number', result_tuple[3]))
    variables.append(('lift', result_tuple[4]))
    variables.append(('duration', result_tuple[5]))
    variables.append(('peak_rpm', result_tuple[7]))
    variables.append(('cr', result_tuple[8]))
    variables.append(('clearance', result_tuple[9]))
    variables.append(('redline', result_tuple[10]))
    variables.append(('valve_number', result_tuple[11]))
    variables.append(('exhaust_length', result_tuple[12]))
    variables.append(('name', result_tuple[15]))
    variables.append(('length', result_tuple_2[0]))
    variables.append(('piston', piston_density))
    variables.append(('rod', rod_density))
    variables.append(('crank', crankshaft_density))
    variables.append(('cam', camshaft_density))
    variables.append(('wires', result_tuple_2[1]))
    variables.append(('ignition', result_tuple_2[2]))
    variables.append(('output_cam', result_tuple_2[3]))
    variables.append(('camshaft', result_tuple_2[4]))
    variables.append(('intake_cam', result_tuple_2[5]))
    variables.append(('exhaust_cam', result_tuple_2[6]))
    variables.append(('rod_journal', result_tuple_2[8]))
    variables.append(('add_rod_journal', result_tuple_2[9]))
    variables.append(('crank_angle', -(result_tuple_2[7])))
    variables.append(('cyl_and_bank', result_tuple_2[10]))
    variables.append(('add_bank', result_tuple_2[11]))
    variables.append(('cylinder_head', result_tuple_2[12]))

    variables_mapping = dict(variables)

    return variables_mapping

#creates the actual densities gui
densities = tk.Tk()
densities.title("select part materials. densities are in g/cc in parentheses")

#creates a label for the first dropdown menu
label_1 = tk.Label(densities, text="piston material:")
label_1.pack()

#create the first dropdown menu
options_1 = ["cast steel (7.15)", "aluminum 356 (2.67)", "aluminum 390 (2.72)"]
dropdown_1 = ttk.Combobox(densities, values=options_1)
dropdown_1.pack()

#creates a lbel for the second dropdown menu
label_2 = tk.Label(densities, text="rod material:")
label_2.pack()

# Create the second dropdown menu
options_2 = ["carbon steel (7.84)", "aluminium 2024 (2.78)", "aluminum 7075 (2.81)", "titanium (4.51)", "cast iron (7.13)"]
dropdown_2 = ttk.Combobox(densities, values=options_2)
dropdown_2.pack()

#creates a label for the third dropdown menu
label_3 = tk.Label(densities, text="crankshaft material:")
label_3.pack()

#create the third dropdown menu
options_3 = ["steel (7.85)", "carbon steel (7.84)", "cast iron (7.13)", "titanium (4.51)", "cast iron (7.13)"]
dropdown_3 = ttk.Combobox(densities, values=options_3)
dropdown_3.pack()

#creates a abke foir the fourth dropdown menu
label_4 = tk.Label(densities, text="camshaft material:")
label_4.pack()

#create the fourth dropdown menu
options_4 = ["steel (7.85)", "cast iron (7.13)"]
dropdown_4 = ttk.Combobox(densities, values=options_4)
dropdown_4.pack()

# Bind an event handler to handle selection changes
dropdown_1.bind("<<ComboboxSelected>>", handle_selection)
dropdown_2.bind("<<ComboboxSelected>>", handle_selection)
dropdown_3.bind("<<ComboboxSelected>>", handle_selection)
dropdown_4.bind("<<ComboboxSelected>>", handle_selection)

densities.mainloop()

var_list = [piston_density, rod_density, crankshaft_density, camshaft_density]

    # Check if all variables have a non-None value using a list comprehension and all()
all_have_value = all(var is not None for var in var_list)

    # if previous line returns yes then destrot the densities gui window
if all_have_value:

    variables = generate_variables()

    template_path = get_template_path()

    # Select output path using file dialog
    output_path = select_output_path()

    # Check if output_path is not empty (user canceled file dialog)
    if output_path:
        # Fill the template and save the output
        fill_template(template_path, output_path, **variables)
        print(f"Template filled and saved to '{output_path}'")
    else:
        print("File dialog canceled, operation aborted.")