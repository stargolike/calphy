from lammps import lammps
import time

# Initialize LAMMPS instance
lmp = lammps(cmdargs=["-k", "on", "g", "1", "-sf", "kk", "-pk", "kokkos", "newton", "on", "neigh", "half"])

# Basic simulation settings
lmp.command("units metal")                  # Use metal units (eV, Å, ps, etc.)
lmp.command("boundary p p p")              # Periodic boundaries in x, y, z directions
lmp.command("atom_style atomic")           # Use atomic atom style (no bonds)
lmp.command("timestep 0.001")              # Timestep in picoseconds

# Activate machine learning interatomic potential (MLIAP) support
import lammps.mliap
lammps.mliap.activate_mliappy_kokkos(lmp)

# Configure MACE interatomic potential
lmp.command("pair_style mliap unified /root/test_mace_lammps/MACE-matpes-r2scan-omat-ft.model-mliap_lammps.pt 0")
lmp.command("read_data /root/calphy/examples/example_01/fe-bcc-solid-100-0.0.data")  # Load atomic configuration
lmp.command("pair_coeff * * Fe")          # Assign potential to Fe atoms

# Set atomic mass (Fe-55.845 g/mol)
lmp.command("mass 1 55.845")

# Define custom variables for monitoring
lmp.command("variable mvol equal vol")     # System volume
lmp.command("variable mlx equal lx")       # Box length in x
lmp.command("variable mly equal ly")       # Box length in y
lmp.command("variable mlz equal lz")       # Box length in z
lmp.command("variable mpress equal press") # Pressure

# Initialize atomic velocities with Gaussian distribution
# Use current system time as random seed for reproducibility
random_seed = int(time.time())
lmp.command(f"velocity all create 100.0 {random_seed} dist gaussian")  # 100.0 K initial temperature

# Configure NPT ensemble (isothermal-isobaric)
# Temp: 100 K (target), 0.1 ps thermostat damping
# Pressure: 0 bar (target), 0.1 ps barostat damping
lmp.command("fix nh1 all npt temp 100.0 100.0 0.1 iso 0.0 0.0 0.1")

# Configure thermodynamic output
lmp.command("thermo_style custom step temp press density etotal pe vol lx ly lz")  # Output parameters
lmp.command("thermo 100")                  # Print every 100 steps
lmp.command("thermo_modify flush yes")     # Disable output buffering for real-time logging

# Save thermodynamic data to file

# Equilibration phase: let system stabilize before production run
print("Starting equilibration phase...")
lmp.command("run 5000")  # Run 5000 steps for equilibration

# Reset timestep counter and thermodynamics for production run
lmp.command("reset_timestep 0")
lmp.command("thermo_reset")

# Production simulation phase
print("Starting production simulation...")
lmp.command("run 10000")  # Run 10000 steps for data collection

print("Simulation completed successfully!")