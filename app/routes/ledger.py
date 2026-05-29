from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models.user_data import CarbonRecordModel

bp = Blueprint('ledger', __name__)

CARBON_COEFFICIENTS = {
    '食': {
        '牛肉': {'factor': 27.0, 'suggestion': '牛肉碳排極高，建議一週可安排一天嘗試蔬食！'},
        '豬肉': {'factor': 12.1, 'suggestion': '豬肉碳排偏高，可考慮改吃白肉或蔬食。'},
        '雞肉': {'factor': 6.9, 'suggestion': '雞肉是不錯的蛋白質來源，碳排相對紅肉較低。'},
        '魚肉': {'factor': 6.0, 'suggestion': '魚肉為較低碳選項，建議搭配更多蔬菜。'},
        '蔬食': {'factor': 2.0, 'suggestion': '蔬食是最環保的選擇，感謝您為地球盡一份心力！'}
    },
    '行': {
        '開車': {'factor': 0.25, 'suggestion': '開車碳排較高，建議下次可嘗試搭乘大眾運輸或共乘！'},
        '機車': {'factor': 0.1, 'suggestion': '騎機車雖然方便，短程可以考慮步行或騎腳踏車喔！'},
        '大眾運輸': {'factor': 0.04, 'suggestion': '搭乘大眾運輸是很棒的低碳選擇，請繼續保持！'},
        '步行/腳踏車': {'factor': 0.0, 'suggestion': '零碳排放！對健康與環境都非常好的完美選擇！'}
    },
    '衣': {
        '購買新衣': {'factor': 15.0, 'suggestion': '選擇二手或少買新衣，可有效降低衣著碳足跡。'},
        '購買二手衣': {'factor': 5.0, 'suggestion': '二手衣物已經是更環保的優良選擇。'}
    },
    '住': {
        '家庭用電': {'factor': 0.5, 'suggestion': '關掉不必要的電器與燈光，能幫助節省碳排。'},
        '家庭用水': {'factor': 0.1, 'suggestion': '節省用水也能減少能源消耗。'}
    }
}


@bp.route('/')
@login_required
def index():
    records = CarbonRecordModel.get_by_user_id(g.user['id'])
    total_carbon = sum(r['carbon_amount'] for r in records) if records else 0
    return render_template('index.html', records=records, total_carbon=total_carbon)


@bp.route('/records/new')
@login_required
def new_record():
    return render_template('ledger/record.html')


@bp.route('/records', methods=('POST',))
@login_required
def create_record():
    category = request.form.get('category')
    action_name = request.form.get('action_name')
    parameter_value = request.form.get('parameter_value')

    if not category or not action_name or not parameter_value:
        flash('請填寫所有必填欄位並確保數值格式正確。', 'danger')
        return redirect(url_for('ledger.new_record'))

    try:
        parameter_value = float(parameter_value)
    except ValueError:
        flash('參數值必須為數字', 'danger')
        return redirect(url_for('ledger.new_record'))

    factor_data = CARBON_COEFFICIENTS.get(category, {}).get(action_name)
    if factor_data:
        carbon_amount = parameter_value * factor_data['factor']
        suggestion = factor_data['suggestion']
    else:
        carbon_amount = parameter_value * 1.0
        suggestion = '系統已記錄此項行為。'

    CarbonRecordModel.create({
        'user_id': g.user['id'],
        'category': category,
        'action_name': action_name,
        'parameter_value': parameter_value,
        'carbon_amount': round(carbon_amount, 2),
        'suggestion': suggestion
    })

    flash(f'成功記錄！本次產生了 {carbon_amount:.2f} kg 碳排。', 'success')
    return redirect(url_for('ledger.index'))


@bp.route('/records/<int:record_id>/delete', methods=('POST',))
@login_required
def delete_record(record_id):
    record = CarbonRecordModel.get_by_id(record_id)
    if record and record['user_id'] == g.user['id']:
        CarbonRecordModel.delete(record_id)
        flash('紀錄已刪除。', 'success')
    else:
        flash('無法刪除此紀錄。', 'danger')
    return redirect(url_for('ledger.index'))
