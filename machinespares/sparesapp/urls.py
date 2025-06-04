from django.urls import path
from sparesapp import views


urlpatterns = [

    path('add_machine/', views.add_machine,name='add_machine'),
    path('list_machine/', views.list_machine,name='list_machine'),
    path('add_spares/',views.add_spares,name='add_spares'),
    path('list_spares/',views.list_spares,name='list_spares'),
    # path('add_inward/',views.add_inward,name='add_inward'),
    path('list_inward/',views.list_inward,name='list_inward'),
    path('add_outward/',views.add_outward,name='add_outward'),
    path('list_outward/',views.list_outward,name='list_outward'),
    path('list_stock/',views.list_stock_details,name='list_stock'),
    # path('add-breakdown/<str:machine_id>/', views.add_breakdown, name='add_breakdown'),
    path('machines/<str:machine_id>/details/', views.overall_machine, name='overall_machine'),
    path('spare_detail/<str:spare_id>/', views.spare_detail, name='spare_detail'),
    path('spare_edit/<str:spare_id>/', views.spare_edit, name='spare_edit'),
    path('delete_spare/<str:spare_id>/', views.delete_spare, name='delete_spare'),
    path('spare_add_machine/<str:machine_id>/',views.spare_add,name='spare_add_machine'),
    path('assign-spare/<str:machine_id>/', views.assign_spare_to_machine, name='assign_spare'),
    path('breakdown-detail/<str:breakdown_id>/', views.breakdown_detail_view, name='breakdown_detail_view'),
    path('list_spare/<str:machine_id>/', views.list_spare, name='list_spare'),
    path('machine/<str:machine_id>/breakdowns/', views.list_breakdowns, name='list_breakdowns'),
    path('inwarddetails/<str:id>', views.details_of_inward, name='details_of_inward'),
    path('breakdown_adding/<str:id>', views.breakdown_adding, name='breakdown_adding'),
    path('add_inward/', views.inward_adding, name='add_inward'),
    path('', views.dashboard, name='dashboard'),
    path('breakdownDetails/<str:id>', views.breakdownDetails, name='breakdownDetails'),
    path('breakdown_report1/', views.breakdown_report, name='breakdown_report'),
    path('spares_inward_report1/',views.spares_inward_report,name='spares_inward_report'),
    path('spares_outward_report1/',views.spares_outward_report,name='spares_outward_report'),
    path('spares_outward_report/',views.spares_outward_report2,name='spares_outward_report2'),
    path('check_preventive/<str:id>', views.check_preventive, name='check_preventive'),
    path('detail_preventive/<str:id>', views.detail_preventive, name='detail_preventive'),

    path('upload-image/', views.upload_image, name='upload_image'),
    path('my-images/', views.list_images, name='list_images'),
    path('delete-images/', views.delete_images, name='delete_images'),


    path('add_preventive/',views.add_preventive,name = 'add_preventive'),
    path('list_preventive/',views.list_preventive,name = 'list_preventive'),
    path('breakdown_report/',views.breakdown_report2,name = 'breakdown_report2'),
    path('spares_inward_report/',views.spares_inward_report2,name = 'spares_inward_report2'),


    path('breakdown_adding_production/<str:id>',views.breakdown_adding_production,name = 'breakdown_adding_production'),
    path('update_breakdown/<str:id>',views.update_breakdown,name = 'update_breakdown'),
    path('api/machines/', views.machine_list_api, name='machine-list'),
    path('breakdown_adding_production_api/', views.breakdown_adding_production_api, name='breakdown_adding_production_api'),
    path('send-notification/', views.send_notification_to_all_users),
    path('api/store_fcm_token/', views.store_fcm_token, name='store_fcm_token'),
    path('testing_notifications', views.testing_notifications, name='testing_notifications'),
    # path('testing_2/', views.testing_2, name='testing_2'),
    path('api/breakdowns/', views.list_outward_api, name='list_outward_api'),
    path('api/spares/', views.spares_api, name='spares_api'),
    path('api/breakdowns/fix/<str:id>', views.update_breakdown_api, name='update_breakdown_api'),

    path('api/send-location/', views.receive_location, name='send_location'),

    path('api/register-face/', views.RegisterFaceView.as_view()),
    path('api/auth-face/', views.AuthenticateFaceView.as_view()),

] 
