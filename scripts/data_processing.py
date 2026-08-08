import xlrd
import pandas as pd
from pathlib import Path

def inp(file_name):
	book = xlrd.open_workbook(Path('data/raw') / file_name)
	sheet = book.sheet_by_index(0)

	data = []
	for row in range(sheet.nrows):
		data.append(sheet.row_values(row))

	df = pd.DataFrame(data[1:], columns=data[0])

	df = df.iloc[:, [1, 2]]
	df.columns = ['R, OHM', 'P, mV']
	
	return df


def fill_press(df, fill_direction):
	df['P, mV'] = pd.to_numeric(df['P, mV'], errors='coerce')

	#fill_direction = 'up'
	#fill_direction = 'dn'

	if fill_direction == 'up':
		df['P, mV'] = df['P, mV'].ffill()
	else:
		df['P, mV'] = df['P, mV'].bfill()

	df['block_id'] = (df['P, mV'] != df['P, mV'].shift()).cumsum()

	return df


def avg_last(df):
	return (df.groupby('block_id')
		.apply(lambda df: pd.Series({
			'P, mV': df['P, mV'].iloc[0],
			'R, OHM': df['R, OHM'].tail(25).mean()
		}))
		.reset_index(drop=True))

def save(df, file_name):
	name = Path(file_name).stem
	output_file = Path('data/processed') / f"{name}_averaged.xlsx"
	df.to_excel(output_file, index=False)