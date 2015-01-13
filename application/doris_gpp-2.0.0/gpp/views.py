from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Document
from query_functions import process_query
from django.core.paginator import Paginator
from math import ceil

import logging


def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    context_dict = \
        {'agencies': ['Aging', 'Buildings', 'Campaign Finance', 'Children\'s Services', 'City Council', 'City Clerk',
                      'City Planning', 'Citywide Admin Svcs', 'Civilian Complaint', 'Comm - Police Corr',
                      'Community Assistance', 'Comptroller', 'Conflicts of Interest', 'Consumer Affairs', 'Contracts',
                      'Correction', 'Criminal Justice Coordinator', 'Cultural Affairs', 'DOI - Investigation',
                      'Design/Construction', 'Disabilities', 'District Atty, NY County', 'Districting Commission',
                      'Domestic Violence', 'Economic Development', 'Education, Dept. of', 'Elections, Board of',
                      'Emergency Mgmt.', 'Employment', 'Empowerment Zone', 'Environmental - DEP', 'Environmental - OEC',
                      'Environmental - ECB', 'Equal Employment', 'Film/Theatre', 'Finance', 'Fire', 'FISA',
                      'Health and Mental Hyg.', 'HealthStat', 'Homeless Services', 'Hospitals - HHC', 'Housing - HPD',
                      'Human Rights', 'Human Rsrcs - HRA', 'Immigrant Affairs', 'Independent Budget',
                      'Info. Tech. and Telecom.', 'Intergovernmental', 'International Affairs', 'Judiciary Committee',
                      'Juvenile Justice', 'Labor Relations', 'Landmarks', 'Law Department', 'Library - Brooklyn',
                      'Library - New York', 'Library - Queens', 'Loft Board', 'Management and Budget', 'Mayor',
                      'Metropolitan Transportation Authority', 'NYCERS', 'Operations', 'Parks and Recreation',
                      'Payroll Administration', 'Police', 'Police Pension Fund', 'Probation', 'Public Advocate',
                      'Public Health', 'Public Housing-NYCHA', 'Records', 'Rent Guidelines', 'Sanitation',
                      'School Construction', 'Small Business Svcs', 'Sports Commission', 'Standards and Appeal',
                      'Tax Appeals Tribunal', 'Tax Commission', 'Taxi and Limousine', 'Transportation',
                      'Trials and Hearings', 'Veterans - Military', 'Volunteer Center', 'Voter Assistance',
                      'Youth & Community'],
         'categories': ['Business and Consumers', 'Cultural/Entertainment', 'Education', 'Environment',
                        'Finance and Budget', 'Government Policy', 'Health', 'Housing and Buildings', 'Human Services',
                        'Labor Relations', 'Public Safety', 'Recreation/Parks', 'Sanitation', 'Technology',
                        'Transportation'],
         'types': ['Annual Report', 'Audit Report', 'Bond Offering - Official Statements', 'Budget Report',
                   'Consultant Report', 'Guide - Manual', 'Hearing - Minutes', 'Legislative Document',
                   'Memoranda - Directive', 'Press Release', 'Serial Publication', 'Staff Report', 'Report'], }
    request.session.flush()
    return render_to_response('index.html', context_dict, context)


def results(request):
    context = RequestContext(request)
    if not request.session.get('num_results'):
        request.session['num_results'] = 10
    if not request.session.get('sort'):
        request.session['sort'] = 'Relevance'
    if not request.session.get('list_view'):
        request.session['list_view'] = 0
    if not request.session.get('start'):
        request.session['start'] = 0
    if not request.session.get('page'):
        request.session['page'] = 1

    # On GET Request
    if request.method == 'GET':
        request.session['page'] = 1
        request.session['start'] = 0
        if request.GET.get('btn') == "Search":
            request.session['search'] = request.GET.get('user_input')
            request.session['agencies'] = request.GET.getlist('agency[]', None)
            request.session['categories'] = request.GET.getlist('category[]', None)
            request.session['types'] = request.GET.getlist('type[]', None)
            request.session['fulltext'] = request.GET.get('fulltext', False)

        # #POST - Refine Search
        if request.GET.get('btn') == "Refine / Search":
            if request.GET.get('user_input'):
                request.session['search'] = request.GET.get('user_input')
            request.session['agencies'] = request.GET.getlist('agency[]')
            request.session['categories'] = request.GET.getlist('category[]')
            request.session['types'] = request.GET.getlist('type[]')
            request.session['fulltext'] = request.GET.get('fulltext', False)
        # GET - Sort
        request.session['sort'] = request.GET.get('sort', request.session.get('sort'))
        # GET - Num Results
        request.session['num_results'] = request.GET.get('num_results', request.session.get('num_results'))
        # GET - List view
        request.session['list_view'] = request.GET.get('list_view', request.session.get('list_view'))
        request.session['page'] = request.GET.get('page', request.session.get('page'))
        request.session['start'] = int(request.session['num_results']) * (int(request.session['page']) - 1)
    else:
        return HttpResponse(status=404)

    # retrieve results
    request.session['results_list'], results_length, \
                    query_time = process_query(
                        request.session.get('search'),
                        request.session.get('agencies'),
                        request.session.get('categories'),
                        request.session.get('types'),
                        request.session.get('fulltext'),
                        request.session.get('start'),
                        int(request.session.get('num_results')),
                        request.session.get('sort'))

    request.session['length'] = results_length
    request.session['num_pages'] = int(ceil(request.session['length'] / float(request.session['num_results'])))
    # initiate pagination
    # print num_results
    paginator = Paginator(range(1, request.session['length'] + 1), request.session.get('num_results'))
    pag_res = paginator.page(request.session['page'])
    # print pag_res
    context_dict = {'results': request.session['results_list'],
                    'agencies': ['Aging', 'Buildings', 'Campaign Finance', 'Children\'s Services', 'City Council',
                                 'City Clerk', 'City Planning', 'Citywide Admin Svcs', 'Civilian Complaint',
                                 'Comm - Police Corr', 'Community Assistance', 'Comptroller', 'Conflicts of Interest',
                                 'Consumer Affairs', 'Contracts', 'Correction', 'Criminal Justice Coordinator',
                                 'Cultural Affairs', 'DOI - Investigation', 'Design/Construction', 'Disabilities',
                                 'District Atty, NY County', 'Districting Commission', 'Domestic Violence',
                                 'Economic Development', 'Education, Dept. of', 'Elections, Board of',
                                 'Emergency Mgmt.', 'Employment', 'Empowerment Zone', 'Environmental - DEP',
                                 'Environmental - OEC', 'Environmental - ECB', 'Equal Employment', 'Film/Theatre',
                                 'Finance', 'Fire', 'FISA', 'Health and Mental Hyg.', 'HealthStat', 'Homeless Services',
                                 'Hospitals - HHC', 'Housing - HPD', 'Human Rights', 'Human Rsrcs - HRA',
                                 'Immigrant Affairs', 'Independent Budget', 'Info. Tech. and Telecom.',
                                 'Intergovernmental', 'International Affairs', 'Judiciary Committee',
                                 'Juvenile Justice', 'Labor Relations', 'Landmarks', 'Law Department',
                                 'Library - Brooklyn', 'Library - New York', 'Library - Queens', 'Loft Board',
                                 'Management and Budget', 'Mayor', 'Metropolitan Transportation Authority', 'NYCERS',
                                 'Operations', 'Parks and Recreation', 'Payroll Administration', 'Police',
                                 'Police Pension Fund', 'Probation', 'Public Advocate', 'Public Health',
                                 'Public Housing-NYCHA', 'Records', 'Rent Guidelines', 'Sanitation',
                                 'School Construction', 'Small Business Svcs', 'Sports Commission',
                                 'Standards and Appeal', 'Tax Appeals Tribunal', 'Tax Commission', 'Taxi and Limousine',
                                 'Transportation', 'Trials and Hearings', 'Veterans - Military', 'Volunteer Center',
                                 'Voter Assistance', 'Youth & Community'],
                    'categories': ['Business and Consumers', 'Cultural/Entertainment', 'Education', 'Environment',
                                   'Finance and Budget', 'Government Policy', 'Health', 'Housing and Buildings',
                                   'Human Services', 'Labor Relations', 'Public Safety', 'Recreation/Parks',
                                   'Sanitation', 'Technology', 'Transportation'],
                    'types': ['Annual Report', 'Audit Report', 'Bond Offering - Official Statements', 'Budget Report',
                              'Consultant Report', 'Guide - Manual', 'Hearing - Minutes', 'Legislative Document',
                              'Memoranda - Directive', 'Press Release', 'Serial Publication', 'Staff Report', 'Report'],
                    'length': int(request.session.get('length')),
                    'search': str(request.session.get('search')),
                    'pag_res': pag_res,
                    'num_results': int(request.session.get('num_results')),
                    'time': query_time,
                    'sort_method': request.session.get('sort'),
                    'list_view': int(request.session.get('list_view')),
                    'records': range(1, request.session['length'] + 1)}    
    return render_to_response('results.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    return render_to_response('about.html', context)


def publication(request):
    context = RequestContext(request)
    print context
    id = request.POST['view']
    # print id
    if id:
        document_url = Document.objects.filter(id=id)[0].url
    else:
        document_url = ''
    # print id, document_url
    context_dict = {'id': id,
                    'document_url': document_url}
    return render_to_response('publication.html', context_dict, context)
