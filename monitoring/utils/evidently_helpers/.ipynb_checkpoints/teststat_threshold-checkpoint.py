import warnings
warnings.simplefilter("ignore")

def check_suitable_drift_threshold(
    reference_data,
    current_pool_data,
    column_mapping,
    current_start = '2016-01-01',
    current_end = '2017-01-01',
    check_period = 7,
    drop_last = True,
):

    target_drifts_list = []
    prediction_drifts_list = []

    start_date = pd.to_datetime(current_start)
    year = int(current_end[:4])
    is_stop = False

    while True:
        end_date = start_date + pd.Timedelta(days=check_period)

        if end_date.year > year - 1:
            end_date = pd.to_datetime(current_end)
            is_stop = True

        current_data = current_pool_data.loc[
            current_pool_data[DATE_TIME_COLUMN].between(
                start_date, end_date, inclusive="left"
            )
        ].copy()
    
        report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
        result = report.as_dict()

        prediction_drifts_list.append(
            result['metrics'][0]['result']['drift_score']
        )
        target_drifts_list.append(
            result['metrics'][1]['result']['drift_score']
        )

        print(start_date, "->", end_date)

        start_date = end_date

        if is_stop:
            break
            
    if drop_last:
        target_drifts_list.pop()
        prediction_drifts_list.pop()
        
    return target_drifts_list, prediction_drifts_list