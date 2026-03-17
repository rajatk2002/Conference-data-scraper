from django.shortcuts import render
from django.db.models import Q
from .models import ConferenceItem
from django.core.paginator import Paginator
from django.http import HttpResponse

import csv
import pandas as pd
from openpyxl import Workbook


def home(request):
    return render(request,"home.html")


def dashboard(request):

    total_sessions = ConferenceItem.objects.filter(session_type="Session").count()

    total_posters = ConferenceItem.objects.filter(session_type="Poster").count()

    total_authors = ConferenceItem.objects.values('authors').count()

    context = {
        "sessions": total_sessions,
        "posters": total_posters,
        "authors": total_authors
    }

    return render(request, "dashboard.html", context)


def records(request):
    search_query = request.GET.get("search", "")
    type_filter = request.GET.get("type", "")
    limit = request.GET.get("limit", 25)

    data = ConferenceItem.objects.all()

    if search_query:
        data = data.filter(
            Q(session_title__icontains=search_query) |
            Q(authors__icontains=search_query) |
            Q(affiliations__icontains=search_query) |
            Q(session_category__icontains=search_query)
        )

    if type_filter:
        data = data.filter(session_type=type_filter)

    paginator = Paginator(data, limit)

    page_number = request.GET.get("page", 1)
    records = paginator.get_page(page_number)

    start_index = records.start_index()
    end_index = records.end_index()
    total_records = paginator.count

    context = {
        "records": records,
        "search_query": search_query,
        "type_filter": type_filter,
        "limit": int(limit),
        "start_index": start_index,
        "end_index": end_index,
        "total_records": total_records,
    }

    return render(request, "records.html", context)


def get_filtered_records(request):
    search = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')

    records = ConferenceItem.objects.all()

    if search:
        records = records.filter(
            Q(session_title__icontains=search) |
            Q(authors__icontains=search) |
            Q(affiliations__icontains=search) |
            Q(session_category__icontains=search)
        )

    if type_filter:
        records = records.filter(session_type=type_filter)

    return records


def export_csv(request):
    records = get_filtered_records(request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="conference_records.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Type', 'Date', 'Time', 'Location', 'Authors'])

    for record in records:
        writer.writerow([
            record.session_title,
            record.session_type,
            record.date,
            record.time,
            record.location,
            record.authors
        ])

    return response


def export_excel(request):
    records = get_filtered_records(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Conference Records"

    ws.append(['Title', 'Type', 'Date', 'Time', 'Location', 'Authors'])

    for record in records:
        ws.append([
            record.session_title,
            record.session_type,
            record.date,
            record.time,
            record.location,
            record.authors
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=conference_records.xlsx'

    wb.save(response)
    return response