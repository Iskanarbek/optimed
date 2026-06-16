from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin Panel
    path('', views.admin_panel, name='admin_panel'),
    path('service/add/', views.add_service, name='add_service'),
    path('service/edit/<int:pk>/', views.edit_service, name='edit_service'),
    path('service/delete/<int:pk>/', views.delete_service, name='delete_service'),
    path('worker/add/', views.add_worker, name='add_worker'),
    path('worker/edit/<int:pk>/', views.edit_worker, name='edit_worker'),
    path('worker/delete/<int:pk>/', views.delete_worker, name='delete_worker'),

    # Glasses (Admin)
    path('glasses/add/', views.add_glasses, name='add_glasses'),
    path('glasses/edit/<int:pk>/', views.edit_glasses, name='edit_glasses'),
    path('glasses/delete/<int:pk>/', views.delete_glasses, name='delete_glasses'),

    # Expenses
    path('expense/add/', views.add_expense, name='add_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),

    # Referral Partners
    path('referral/add/', views.add_referral_partner, name='add_referral_partner'),
    path('referral/edit/<int:pk>/', views.edit_referral_partner, name='edit_referral_partner'),
    path('referral/delete/<int:pk>/', views.delete_referral_partner, name='delete_referral_partner'),

    # Analytics
    path('analytics/overall/', views.analytics_overall, name='analytics_overall'),
    path('analytics/services/', views.analytics_services, name='analytics_services'),
    path('analytics/doctors/', views.analytics_doctors, name='analytics_doctors'),
    path('analytics/referrals/', views.analytics_referrals, name='analytics_referrals'),
    path('analytics/glasses/', views.analytics_glasses, name='analytics_glasses'),

    # Admin patient detail
    path('panel/patient/<int:patient_id>/', views.admin_patient_detail, name='admin_patient_detail'),

    # Data Export
    path('export/data/', views.export_data_excel, name='export_data_excel'),
    path('export/pdf/', views.export_data_pdf, name='export_data_pdf'),

    # Receptionist
    path('receptionist/', views.receptionist_panel, name='receptionist_panel'),
    path('receptionist/add/', views.add_patient, name='add_patient'),
    path('receptionist/edit/<int:pk>/', views.edit_patient, name='edit_patient'),
    path('receptionist/delete/<int:pk>/', views.delete_patient, name='delete_patient'),
    path('receptionist/redirect/<int:pk>/', views.redirect_patient, name='redirect_patient'),
    path('receptionist/visit/<int:visit_id>/edit/', views.receptionist_edit_visit, name='receptionist_edit_visit'),
    path('receptionist/notifications/', views.receptionist_notifications, name='receptionist_notifications'),
    path('receptionist/rate/<int:pk>/', views.rate_visit, name='rate_visit'),
    path('receptionist/procedures/', views.receptionist_procedures, name='receptionist_procedures'),
    path('receptionist/notify/<int:pk>/', views.notify_procedure, name='notify_procedure'),
    path('receptionist/ticket/<int:visit_id>/', views.receptionist_print_ticket, name='receptionist_print_ticket'),
    path('receptionist/lab-ticket/<int:lab_visit_id>/', views.receptionist_print_lab_ticket, name='receptionist_print_lab_ticket'),
    path('receptionist/history/', views.receptionist_history, name='receptionist_history'),
    path('receptionist/history/patient/<int:patient_id>/', views.receptionist_patient_history, name='receptionist_patient_history'),
    path('receptionist/history/doctor/<int:doctor_id>/', views.receptionist_doctor_history, name='receptionist_doctor_history'),
    path('receptionist/history/orphan/', views.receptionist_orphan_visits, name='receptionist_orphan_visits'),
    path('receptionist/history/reassign/', views.receptionist_reassign_doctor, name='receptionist_reassign_doctor'),

    # Scheduling
    path('receptionist/schedule/', views.receptionist_schedule, name='receptionist_schedule'),
    path('receptionist/schedule/add/', views.add_scheduled_visit, name='add_scheduled_visit'),
    path('receptionist/schedule/activate/<int:pk>/', views.activate_scheduled_visit, name='activate_scheduled_visit'),
    path('receptionist/schedule/edit/<int:pk>/', views.edit_scheduled_visit, name='edit_scheduled_visit'),
    path('receptionist/schedule/delete/<int:pk>/', views.delete_scheduled_visit, name='delete_scheduled_visit'),

    # Doctor
    path('doctor/<int:doctor_id>/', views.doctor_panel, name='doctor_panel'),
    path('doctor/<int:doctor_id>/patient/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/<int:doctor_id>/patient/<int:patient_id>/full-history/', views.doctor_patient_full_history, name='doctor_patient_full_history'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/', views.doctor_visit_detail, name='doctor_visit_detail'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/update/', views.doctor_update_visit, name='doctor_update_visit'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/complete/', views.doctor_complete_visit, name='doctor_complete_visit'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/procedure/', views.doctor_add_procedure, name='doctor_add_procedure'),
    path('doctor/<int:doctor_id>/procedure/<int:procedure_id>/edit/', views.doctor_edit_procedure, name='doctor_edit_procedure'),
    path('doctor/<int:doctor_id>/procedure-date/<int:pd_id>/complete/', views.doctor_complete_procedure_date, name='doctor_complete_procedure_date'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/edit-done/', views.doctor_edit_done_visit, name='doctor_edit_done_visit'),
    path('doctor/<int:doctor_id>/attachment/<int:att_id>/delete/', views.doctor_delete_attachment, name='doctor_delete_attachment'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/receipt/', views.doctor_visit_receipt, name='doctor_visit_receipt'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/medical-notes/', views.doctor_medical_notes, name='doctor_medical_notes'),

    # Doctor: Eye examination data
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/refraction/add/', views.doctor_add_refraction, name='doctor_add_refraction'),
    path('doctor/<int:doctor_id>/refraction/<int:pk>/edit/', views.doctor_edit_refraction, name='doctor_edit_refraction'),
    path('doctor/<int:doctor_id>/refraction/<int:pk>/delete/', views.doctor_delete_refraction, name='doctor_delete_refraction'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/krt/add/', views.doctor_add_krt, name='doctor_add_krt'),
    path('doctor/<int:doctor_id>/krt/<int:pk>/edit/', views.doctor_edit_krt, name='doctor_edit_krt'),
    path('doctor/<int:doctor_id>/krt/<int:pk>/delete/', views.doctor_delete_krt, name='doctor_delete_krt'),
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/iop/add/', views.doctor_add_iop, name='doctor_add_iop'),
    path('doctor/<int:doctor_id>/iop/<int:pk>/edit/', views.doctor_edit_iop, name='doctor_edit_iop'),
    path('doctor/<int:doctor_id>/iop/<int:pk>/delete/', views.doctor_delete_iop, name='doctor_delete_iop'),

    # Visual acuity
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/visual-acuity/add/', views.doctor_add_visual_acuity, name='doctor_add_visual_acuity'),
    path('doctor/<int:doctor_id>/visual-acuity/<int:pk>/edit/', views.doctor_edit_visual_acuity, name='doctor_edit_visual_acuity'),
    path('doctor/<int:doctor_id>/visual-acuity/<int:pk>/delete/', views.doctor_delete_visual_acuity, name='doctor_delete_visual_acuity'),
    # Eye exam
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/eye-exam/add/', views.doctor_add_eye_exam, name='doctor_add_eye_exam'),
    path('doctor/<int:doctor_id>/eye-exam/<int:pk>/edit/', views.doctor_edit_eye_exam, name='doctor_edit_eye_exam'),
    path('doctor/<int:doctor_id>/eye-exam/<int:pk>/delete/', views.doctor_delete_eye_exam, name='doctor_delete_eye_exam'),
    # Discharge
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/discharge/add/', views.doctor_add_discharge, name='doctor_add_discharge'),
    path('doctor/<int:doctor_id>/discharge/<int:pk>/edit/', views.doctor_edit_discharge, name='doctor_edit_discharge'),
    path('doctor/<int:doctor_id>/discharge/<int:pk>/delete/', views.doctor_delete_discharge, name='doctor_delete_discharge'),
    # LASIK
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/lasik/add/', views.doctor_add_lasik, name='doctor_add_lasik'),
    path('doctor/<int:doctor_id>/lasik/<int:pk>/edit/', views.doctor_edit_lasik, name='doctor_edit_lasik'),
    path('doctor/<int:doctor_id>/lasik/<int:pk>/delete/', views.doctor_delete_lasik, name='doctor_delete_lasik'),
    # Strabismus
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/strabismus/add/', views.doctor_add_strabismus, name='doctor_add_strabismus'),
    path('doctor/<int:doctor_id>/strabismus/<int:pk>/edit/', views.doctor_edit_strabismus, name='doctor_edit_strabismus'),
    path('doctor/<int:doctor_id>/strabismus/<int:pk>/delete/', views.doctor_delete_strabismus, name='doctor_delete_strabismus'),
    # PostOp
    path('doctor/<int:doctor_id>/visit/<int:visit_id>/postop/add/', views.doctor_add_postop, name='doctor_add_postop'),
    path('doctor/<int:doctor_id>/postop/<int:pk>/edit/', views.doctor_edit_postop, name='doctor_edit_postop'),
    path('doctor/<int:doctor_id>/postop/<int:pk>/delete/', views.doctor_delete_postop, name='doctor_delete_postop'),
    # Receptionist documents & reference
    path('receptionist/reference/', views.receptionist_reference_indicators, name='receptionist_reference_indicators'),
    path('receptionist/documents/', views.receptionist_documents, name='receptionist_documents'),
    path('receptionist/documents/search/', views.receptionist_documents_search, name='receptionist_documents_search'),
    path('receptionist/documents/<str:form_type>/<int:pk>/', views.receptionist_document_view, name='receptionist_document_view'),

    # Seller Panel
    path('seller/', views.seller_panel, name='seller_panel'),
    path('seller/add/', views.seller_add_glasses, name='seller_add_glasses'),
    path('seller/edit/<int:pk>/', views.seller_edit_glasses, name='seller_edit_glasses'),
    path('seller/delete/<int:pk>/', views.seller_delete_glasses, name='seller_delete_glasses'),
    path('seller/sell/', views.seller_sell_glasses, name='seller_sell_glasses'),
    path('seller/sales/', views.seller_sales, name='seller_sales'),
    path('seller/analytics/', views.seller_analytics, name='seller_analytics'),

    # Laboratory Panel
    path('lab/', views.lab_panel, name='lab_panel'),
    path('lab/visit/<int:pk>/', views.lab_visit_detail, name='lab_visit_detail'),
    path('lab/visit/<int:pk>/save/', views.lab_save_results, name='lab_save_results'),

    # API
    path('api/analytics/overall/', views.api_analytics_overall, name='api_analytics_overall'),
    path('api/analytics/services/', views.api_analytics_services, name='api_analytics_services'),
    path('api/analytics/doctors/', views.api_analytics_doctors, name='api_analytics_doctors'),
    path('api/patient-search/', views.api_patient_search, name='api_patient_search'),
    path('api/patient/<int:patient_id>/procedures/', views.api_patient_procedures, name='api_patient_procedures'),
    path('api/lab-services/search/', views.api_lab_services_search, name='api_lab_services_search'),
    path('api/check-phone/', views.api_check_phone, name='api_check_phone'),
]
