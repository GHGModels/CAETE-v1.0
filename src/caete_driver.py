#!/usr/local/bin/ipython3
import concurrent.futures as conc
import os
from glob import glob1
from shutil import copyfile

from caete_module import global_pars as gp
from homedir import OUTPUT_NC_DIR, RESULTS_DIR, TMP_DIR, py_executable

ROOT_DIR = os.getcwd()


def make_dir_spe(folder_path):
    try:
        test = os.path.exists(folder_path)
    except:
        print('Error while checking %s' % folder_path)
        #return False
    if test:
        pass
    else:
        os.mkdir(folder_path)
        #return True

make_dir_spe(TMP_DIR)
make_dir_spe(OUTPUT_NC_DIR)
make_dir_spe(RESULTS_DIR)


def sys_tar(duplet):
    os.system('tar -czf %s %s' % duplet)

def cpfile(duplet):
    copyfile(*duplet)

def log_file(f_con):
    descr = input('Descrição: ')
    with open(f_con,mode='a') as fh:
        fh.write('\n\n\n------\n')
        fh.write(descr)
        fh.write('------\n')


def fprocess(npls, run, res, out, pls):
    os.chdir(res)
    # COMPRESS FILES
    files = glob1(os.getcwd(),'*.nc')
    out1  = [n.split('.')[0] + '.tar.gz' for n in files]
    with conc.ThreadPoolExecutor(max_workers=len(files)) as executor:
        for ft in list(zip(out1,files)):
            f = executor.submit(sys_tar,ft)
            #f.result() # uncomment to simulate a serial execution
    # COPY FILES TO FINAL DESTINATION
    tars = glob1(os.getcwd(), '*.tar.gz')
    outputs_folder = out + os.sep + 'out' + str(npls) + '_r' + str(run)
    if not os.path.exists(outputs_folder):
        os.mkdir(outputs_folder)
    outnames = [outputs_folder + os.sep + n for n in tars ]
    with conc.ThreadPoolExecutor(max_workers=len(files)) as executor:
        for ft in list(zip(tars,outnames)):
            f = executor.submit(cpfile,ft)
            #f.result() # uncomment to simulate a serial execution
    os.chdir(TMP_DIR)
    if pls:
        copyfile(ROOT_DIR + os.sep + 'pls_attrs.csv', outputs_folder + os.sep + 'pls_attrs.csv')
    os.system('rm -rf outputs_nc')
    os.chdir(ROOT_DIR)
    os.system('rm -rf TMP_DIR')
    os.system('./clean_out.sh')


def model_driver():
    npls = gp.npls
    q = str(input('modo PFTs? (s or n): ')).lower()
    while True:
        if q == 's':
            comm = '%s caete_pfts.py' % py_executable
            print('Número de Rodadas definido: 1')
            n_runs = 1
            assert npls == 12, 'O modo PFTS precisa ser compilado com npls=12, npls =  %d fornecido' %npls
            break
        elif q == 'n':
            n_runs = int(input('Número de Rodadas: '))
            comm = "%s caete.py" % py_executable
            break
        else:
            print('Por favor, digite s ou n')
            q = str(input('modo PFTs? (s ou n): ')).lower()
            pass

    assert n_runs > 0

    log_file('exec.log')
    for model_run in range(1,n_runs + 1):
        with open('exec.log', mode='a') as fh:
            fh.write('\n\n\t---Rodada n° %d\n\n' % model_run )
        os.system(comm)
        if comm == '%s caete.py' % py_executable:
            fprocess(npls, model_run, res=OUTPUT_NC_DIR, out=RESULTS_DIR, pls=True)            
        os.system('bash clean_dir.sh')

if __name__ == '__main__':
    model_driver()
    os.system('rm -rf %s' % TMP_DIR)
