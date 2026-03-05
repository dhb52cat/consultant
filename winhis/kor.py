import sys
import os

# 添加上级目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from machine_lib import * 
from mylib import *
# TSOps,
s = login()
df = get_datafields(s, dataset_id = 'fundamental94', region='KOR', universe='TOP600', delay=1)
n=df.id+":"+df.description
expStr='A(B/C, D)'
ops='ts_mean, ts_median, ts_max, ts_min, ts_sum, ts_std_dev, ts_returns, ts_scale, ts_max_diff, ts_min_diff, ts_rank, ts_corr, ts_covariance, ts_partial_corr, ts_product, ts_decay_exp_window, ts_decay_linear, ts_zscore, ts_entropy'.split(',')
profit='fnd94_is_gross_inc_q, fnd94_is_oper_inc_q, fnd94_is_net_inc_basic_q, fnd94_is_net_inc_dil_q, fnd94_is_eps_basic_q, fnd94_is_eps_contin_oper_q, fnd94_is_ebit_oper_q, fnd94_is_ebitda_q'.split(',')
asset='fnd94_bs_assets_tot_q, fnd94_bs_eq_tot_q, fnd94_bs_debt_q, fnd94_bs_liabs_tot_q, fnd94_bs_stock_com_q, fnd94_bs_com_eq_apic_q, fnd94_bs_com_eq_retain_earn_q, fnd94_bs_com_eq_for_exch_q, fnd94_bs_com_eq_par_q, fnd94_bs_treas_stk_q, fnd94_des_mkt_cap_q, fnd94_des_net_debt_q, fnd94_rt_com_eq_assets_q, fnd94_rt_debt_com_eq_q, fnd94_rt_assets_com_eq_q'.split(',')
days='30,60,120,250,360'.split(',')
exps=[]
for A in ops:
    for B in profit:
        for C in asset:
            for D in days:
                exps.append(expStr.replace('A',A).replace('B',B).replace('C',C).replace('D',D)) 

fo_alpha_list = []
init_decay=5
for alpha in exps:
    fo_alpha_list.append((alpha, init_decay))
pools = load_task_pool(fo_alpha_list, 10, 10)
multi_simulate(pools, "MARKET", "KOR", "TOP600", 96)