import numpy as np
from michelson_pcell import Michelson as MZI
from siepic import all as pdk
from ipkiss3 import all as i3

# Parameters for the MZI sweep
delay_lengths = [50.0, 75.0, 100.0, 125.0, 150.0]  # Desired delay lengths in micrometers
bend_radius = 5.0
x0 = 40.0
y0 = 20.0
spacing_x = 100.0

insts = dict()
specs = []

# Create the floorplan
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(605.0, 410.0))

# Add the floorplan to the instances dict and place it at (0.0, 0.0)
specs.append(i3.Inst("floorplan", floorplan))
specs.append(i3.Place("floorplan", (0.0, 0.0)))

# Create the MZI sweep
for ind, delay_length in enumerate(delay_lengths):

    if ind == 4:
        x0 += 20.0  # Add extra spacing before the last MZI
    # Instantiate the MZI
    mzi = MZI(
        name=f"Michelson{ind}",
        delay_length=delay_length,
        bend_radius=bend_radius,
    )

    # Calculate the actual delay length and print the results
    right_arm_length = mzi.get_connector_instances()[1].reference.trace_length()
    left_arm_length = mzi.get_connector_instances()[0].reference.trace_length()
    actual_delay_length = right_arm_length - left_arm_length

    print(mzi.name, f"Desired delay length = {delay_length} um", f"Actual delay length = {actual_delay_length} um")

    # Add the MZI to the instances dict and place it
    mzi_cell_name = f"michelson{ind}"
    specs.append(i3.Inst(mzi_cell_name, mzi))
    specs.append(i3.Place(mzi_cell_name, (x0, y0)))

    x0 += spacing_x

# Create the final design with i3.Circuit
cell = i3.Circuit(
    name="EBeam_NicolasCasteleyn_v2",
    specs=specs,
)

# Layout
cell_lv = cell.Layout()
cell_lv.visualize(annotate=True)
cell_lv.write_gdsii("EBeam_NicolasCasteleyn_v2.gds")

# Circuit model
cell_cm = cell.CircuitModel()
wavelengths = np.linspace(1.52, 1.58, 4001)
S_total = cell_cm.get_smatrix(wavelengths=wavelengths)

if __name__ == "__main__":
    # Plotting
    for ind, delay_length in enumerate(delay_lengths):
        S_total.visualize(
            term_pairs=[(f"mzi{ind}_in:0", f"mzi{ind}_out1:0"), (f"mzi{ind}_in:0", f"mzi{ind}_out2:0")],
            title=f"MZI{ind} - Delay length {delay_length} um",
            scale="dB",
        )

    print("Done")