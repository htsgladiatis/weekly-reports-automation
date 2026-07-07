# Bugfix Requirements Document

## Introduction

Исправление ошибочного расчета итоговой суммы расходов в отчете за период 01.06-07.06.2026. Система некорректно суммирует расходы всех четырех аккаунтов Яндекс.Директ, хотя фактические расходы были только у одного аккаунта (e-20010227 = 27,564₽). Три других аккаунта (e-17228851, dune-group, porg-3uieikjn) имеют нулевые расходы.

Ошибка приводит к искажению финансовых показателей в отчете: ИТОГО показывает 96,494₽ вместо правильных 27,564₽, что может привести к неверным бизнес-решениям.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN система суммирует расходы по четырем аккаунтам (e-20010227=27564₽, e-17228851=58292₽, dune-group=4707₽, porg-3uieikjn=5931₽) THEN система использует значения из комментариев кода (27564 + 58292 + 4707 + 5931 = 96494₽) вместо реальных данных из скриншотов

1.2 WHEN в строке "Итого" рассчитывается общий расход THEN отображается неверное значение 96,494₽

1.3 WHEN в строке "Яндекс Директ" (сводная по всем аккаунтам) рассчитывается расход THEN отображается неверное значение 96,494₽

1.4 WHEN рассчитываются производные метрики (CPC, CPA, CPL) для строк "Итого" и "Яндекс Директ" THEN они используют ошибочную сумму 96,494₽ в расчетах

### Expected Behavior (Correct)

2.1 WHEN система суммирует расходы по четырем аккаунтам THEN система SHALL использовать фактические данные из скриншотов: e-20010227=27564₽, e-17228851=0₽, dune-group=0₽, porg-3uieikjn=0₽, итого = 27,564₽

2.2 WHEN в строке "Итого" рассчитывается общий расход THEN система SHALL отображать 27,564₽ (сумма расходов всех аккаунтов, включая SEO и Рекомендации с нулевыми расходами)

2.3 WHEN в строке "Яндекс Директ" (сводная) рассчитывается расход THEN система SHALL отображать 27,564₽ (сумма расходов четырех аккаунтов Директа)

2.4 WHEN рассчитываются производные метрики для строк "Итого" и "Яндекс Директ" THEN система SHALL использовать правильную сумму 27,564₽: CPC=27564/1541≈18₽, CPA=27564/11≈2506₽, CPL=27564/7≈3938₽

### Unchanged Behavior (Regression Prevention)

3.1 WHEN отображаются данные аккаунта e-20010227 (показы=49416, клики=805, расход=27564₽) THEN система SHALL CONTINUE TO отображать эти значения корректно

3.2 WHEN рассчитываются метрики для отдельных кампаний внутри каждого аккаунта THEN система SHALL CONTINUE TO рассчитывать их на основе данных кампаний

3.3 WHEN отображаются данные аккаунтов e-17228851, dune-group, porg-3uieikjn с нулевыми расходами THEN система SHALL CONTINUE TO корректно показывать их клики и нулевые расходы

3.4 WHEN рассчитываются показатели для строки SEO (80 визитов, 0 лидов) THEN система SHALL CONTINUE TO отображать эти данные без изменений

3.5 WHEN рассчитываются показатели для строки "Рекомендации" THEN система SHALL CONTINUE TO отображать эти данные без изменений

3.6 WHEN форматируются ячейки и применяется форматирование Google Sheets THEN система SHALL CONTINUE TO применять форматирование согласно BOLD_ROWS

## Bug Condition and Property

### Bug Condition Function

```pascal
FUNCTION isBugCondition(accountsData)
  INPUT: accountsData = {
    e-20010227: {spend: Number, clicks: Number, impressions: Number},
    e-17228851: {spend: Number, clicks: Number, impressions: Number},
    dune-group: {spend: Number, clicks: Number, impressions: Number},
    porg-3uieikjn: {spend: Number, clicks: Number, impressions: Number}
  }
  OUTPUT: boolean
  
  // Bug condition: используются значения из комментариев вместо реальных данных
  // Возвращает true когда хотя бы один аккаунт имеет расход=0 в реальных данных,
  // но в расчете используется ненулевое значение
  hasZeroSpendInRealData ← (accountsData[e-17228851].spend = 0) OR 
                            (accountsData[dune-group].spend = 0) OR 
                            (accountsData[porg-3uieikjn].spend = 0)
  
  calculatedTotal ← sum of all accountsData[*].spend from code comments
  
  RETURN hasZeroSpendInRealData AND (calculatedTotal ≠ accountsData[e-20010227].spend)
END FUNCTION
```

### Property: Fix Checking

```pascal
// Property: Correct Total Spend Calculation
FOR ALL accountsData WHERE isBugCondition(accountsData) DO
  totalSpend ← calculateTotalSpend'(accountsData)
  expectedSpend ← sum of actual accountsData[*].spend from screenshots
  
  ASSERT totalSpend = expectedSpend
  ASSERT totalSpend = 27564  // for the specific case 01.06-07.06
  ASSERT (totalSpend displayed in "Итого" row) = "р.27 564"
  ASSERT (totalSpend displayed in "Яндекс Директ" row) = "р.27 564"
END FOR
```

### Property: Preservation Checking

```pascal
// Property: Non-buggy calculations remain unchanged
FOR ALL calculations WHERE NOT isBugCondition(accountsData) DO
  // Расчет отдельных метрик аккаунтов
  ASSERT calculateAccountMetrics(F, account) = calculateAccountMetrics(F', account)
  
  // Расчет метрик кампаний
  ASSERT calculateCampaignMetrics(F, campaign) = calculateCampaignMetrics(F', campaign)
  
  // Форматирование и структура отчета
  ASSERT reportStructure(F) = reportStructure(F')
END FOR
```

### Concrete Counterexample

**Входные данные (из скриншотов):**
```
e-20010227: spend=27564₽, clicks=805, impressions=49416
e-17228851: spend=0₽, clicks=405, impressions=58292
dune-group: spend=0₽, clicks=151, impressions=4707
porg-3uieikjn: spend=0₽, clicks=120, impressions=5931
```

**Текущий (дефектный) вывод F:**
```
Итого: Расход = р.96 494
Яндекс Директ: Расход = р.96 494
```

**Ожидаемый (правильный) вывод F':**
```
Итого: Расход = р.27 564
Яндекс Директ: Расход = р.27 564
```
