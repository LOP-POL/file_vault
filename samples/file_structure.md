The shown in [section2](#Section2)  file structure is for the folder `transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.`
I want you to run the domain cut at x-50 y-50 and then [data2vtk](<#Section 4>) inorder to get the stress data for stress11 stress22 and stress21 , the stress files as saved in the file struecture in the form  `` transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_stress11.p3s`` , for the other folders like this one.
Each folder has a similar naming scheme only the angles and chi value change.
The stress domain cut will give you a new stress output file in that domain and then data2vtk will produce vtk files.
Then once the vtk files are created you have to  create a python file that will us ethe stress data in the  vtk file to plot the stress at that angle and chi value.

I will  place the bash script in side  of the directory that has the output folders. and I will provide the path of the python file to be used.
This bash file  will go through each folder extract the chi and angle values , create the domain cuts then the vtk files from teh domain cuts.
Run the python script to generate the three plots for stress11 stress22 and stress 21 in x y and z , name the plot with the chi value, angle and dimension , I will aslo provide the output for the plot that will be created for each folder . then move on to the next folder.


# Section 2:

## The structure of the folder

```bash
stud-uyslf@izbs-tf-189:/mnt/data/stud-uyslf/code/to_Leon/Tests/data/No_Crack_results/transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43$ ls
transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.infile_saved               transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_pressure.p3s  transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_stress12.p3s
transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.p3simgeo                   transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_strain11.p3s  transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_stress22.p3s
transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.p3timestep                 transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_strain12.p3s  transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_Ux.p3s
transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_energy.p3s  transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_strain22.p3s  transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_Uy.p3s
transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_mises.p3s   transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43.SolidMechanics_stress11.p3s
```

# Section 3:

## Domain cut

```Shell

DESCRIPTION:
domaincut cuts a cube out of the simulation domain.
Release Version 2.6.2 (29.02.2025)


USAGE: domaincut [-bf] [-x|--xoffset [4mlong[0m] [-X|--xend [4mlong[0m] [-y|--yoffset [4mlong[0m] [-Y|--yend [4mlong[0m] [-z|--zoffset [4mlong[0m] [-Z|--zend [4mlong[0m] [-B|--blocksize [4mlong[0m] [-F|--frames [4mframe[0m] filein fileout


OPTIONS:

 <inputfile> (required)
                The simulation file for cutting

 <outputfile> (required)
                The file with the cutted cube

 -b --boundary
                performes a normal boundary cut, cuts off 1 bundary cell on each side of the frame 'cube'
                if possible

 -x<i> --xoffset=<i> (default=0) 
                removes all cells in x dimension outside of [x..X]. Default is to keep all. 0 <= x <= X
                <= Xmax

 -X<i> --xend=<i> (default=-1) 
                removes all cells in x dimension outside of [x..X]. Default is to keep all. 0 <= x <= X
                <= Xmax

 -y<i> --yoffset=<i> (default=0) 
                removes all cells in y dimension outside of [y..Y]. Default is to keep all. 0 <= y <= Y
                <= Ymax

 -Y<i> --yend=<i> (default=-1) 
                removes all cells in y dimension outside of [y..Y]. Default is to keep all. 0 <= y <= Y
                <= Ymax

 -z<i> --zoffset=<i> (default=0) 
                removes all cells in z dimension outside of [z..Z]. Default is to keep all. 0 <= z <= Z
                <= Zmax

 -Z<i> --zend=<i> (default=-1) 
                removes all cells in z dimension outside of [z..Z]. Default is to keep all. 0 <= z <= Z
                <= Zmax

 -B<i> --blocksize=<i> (default=6) 
                Set blocksize of the generated blockdata-file

 -F<i>,<i>-<i>,<i>-<i>%<i> --frames=<i>,<i>-<i>,<i>-<i>%<i>
                Working frames

 -f --force
                force replacement of existing files

 -v<i> --verbose=<i>
                enable the output (stderr) of some (helpful) log messages with log-level <i>, a higher
                level <i> will create more messages.

 -h --help
                print this help (--helpall prints an extended help)

EXAMPLE:
e.g.: domaincut input.phi_alpha.p3s output.phi_alpha.p3s -b
This will cut off the boundary cells and writes the new scalardata to output.phi_alpha.p3s.
e.g.: domaincut input.fluiddynamics_velocity.p3v output.fluiddynamics_velocity.p3v -x 10 -X 50 -z
12
This will cut off all outside the cube[x,y,z](10,0,12) : [X,Y,Z](50,99,99) with a cube containing
100 cells in every dimension.
```

# Section 4

## data2vtk

```Shell

DESCRIPTION:
Converts scalar and/of vector data given by a list of files into VTK format, e.g. for ParaView.
Release Version 2.6.2 (29.02.2025)


USAGE: data2vtk [-aj] [-d|--datafiles [4mtokenlist[0m] [-F|--frames [4mframe[0m] filein fileout


OPTIONS:

 <inputfile> (required)
                The input SimGeo/file of the simulation to process

 <outputfile> (required)
                The name for the output VTK file

 -d<s>%c<s>%c...%c<s> --datafiles=<s>%c<s>%c...%c<s>
                List of scalar/vector files to process

 -a --ascii (default=true) 
                Use ASCII output

 -F<i>,<i>-<i>,<i>-<i>%<i> --frames=<i>,<i>-<i>,<i>-<i>%<i>
                Set number of frames, default for all frames

 -j --writejson (default=true) 
                Write json-metadata file

 -v<i> --verbose=<i>
                enable the output (stderr) of some (helpful) log messages with log-level <i>, a higher
                level <i> will create more messages.

 -h --help
                print this help (--helpall prints an extended help)

EXAMPLE:
e.g.: data2vtk example.p3simgeo out
converts all frames of all saved files of the simulation set to out-###.vtk
e.g.: data2vtk example.phi_alpha.p3s out
converts the phases alpha into file out-phi_alpha-###.vtk
e.g.: data2vtk example.p3simgeo -d "example.phi_alpha.p3s; example.phi_beta.p3s;
example.phi_liquid.p3s" out
converts all frames of the scalar phi-fields of phases alpha, beta and liquid into files
out-###.vtk
e.g.: data2vtk example.p3simgeo -d "example.fluiddynamics_velocity.p3v; example.phi_alpha.p3s;
example.fluiddynamics_pressure.p3s" -F 200 out
converts the vectordata velocity and the scalardata phi_alpha and fluiddynamics_pressure for frame
200 into file out-200.vtk
```
