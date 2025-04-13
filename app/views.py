import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, F, ExpressionWrapper, FloatField
from .models import  CalculationHistory, SustainabilityProfile
from django.core.paginator import Paginator
from datetime import datetime
# Helper function to get or create user profile
def get_user_profile(user):
    profile, created = SustainabilityProfile.objects.get_or_create(
        user=user,
        defaults={'company_name': user.username}
    )
    return profile

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')
#Registration page for the user.
def register(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not all([company_name, username, email, password1, password2]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                profile = get_user_profile(user)
                profile.company_name = company_name
                profile.save()
                
                # Auto-login after registration
                login(request, user)
                messages.success(request, "Registration successful!")
                return redirect('login')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
    
    return render(request, 'register.html')
#Logout function.
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# Other Views
@login_required
def index(request):
    # Dictionary containing SDG titles and descriptions
    sdg_data = {
        1: {"title": "No Poverty", "description": "End poverty in all its forms everywhere.", "link": "https://www.google.com/search?q=SDG+1+No+Poverty"},
        2: {"title": "Zero Hunger", "description": "End hunger, achieve food security and improved nutrition.", "link": "https://www.google.com/search?q=SDG+2+Zero+Hunger"},
        3: {"title": "Good Health and Well-being", "description": "Ensure healthy lives and promote well-being for all.", "link": "https://www.google.com/search?q=SDG+3+Good+Health+and+Well-being"},
        4: {"title": "Quality Education", "description": "Ensure inclusive and equitable quality education.", "link": "https://www.google.com/search?q=SDG+4+Quality+Education"},
        5: {"title": "Gender Equality", "description": "Achieve gender equality and empower all women and girls.", "link": "https://www.google.com/search?q=SDG+5+Gender+Equality"},
        6: {"title": "Clean Water and Sanitation", "description": "Ensure availability and sustainable management of water.", "link": "https://www.google.com/search?q=SDG+6+Clean+Water+and+Sanitation"},
        7: {"title": "Affordable and Clean Energy", "description": "Ensure access to affordable, reliable, and modern energy.", "link": "https://www.google.com/search?q=SDG+7+Affordable+and+Clean+Energy"},
        8: {"title": "Decent Work and Economic Growth", "description": "Promote sustained, inclusive, and sustainable economic growth.", "link": "https://www.google.com/search?q=SDG+8+Decent+Work+and+Economic+Growth"},
        9: {"title": "Industry, Innovation, and Infrastructure", "description": "Build resilient infrastructure and promote industrialization.", "link": "https://www.google.com/search?q=SDG+9+Industry+Innovation+and+Infrastructure"},
        10: {"title": "Reduced Inequality", "description": "Reduce inequality within and among countries.", "link": "https://www.google.com/search?q=SDG+10+Reduced+Inequality"},
        11: {"title": "Sustainable Cities and Communities", "description": "Make cities inclusive, safe, resilient, and sustainable.", "link": "https://www.google.com/search?q=SDG+11+Sustainable+Cities+and+Communities"},
        12: {"title": "Responsible Consumption and Production", "description": "Ensure sustainable consumption and production patterns.", "link": "https://www.google.com/search?q=SDG+12+Responsible+Consumption+and+Production"},
        13: {"title": "Climate Action", "description": "Take urgent action to combat climate change and its impacts.", "link": "https://www.google.com/search?q=SDG+13+Climate+Action"},
        14: {"title": "Life Below Water", "description": "Conserve and sustainably use the oceans, seas, and marine resources.", "link": "https://www.google.com/search?q=SDG+14+Life+Below+Water"},
        15: {"title": "Life on Land", "description": "Protect, restore, and promote sustainable use of terrestrial ecosystems.", "link": "https://www.google.com/search?q=SDG+15+Life+on+Land"},
        16: {"title": "Peace, Justice, and Strong Institutions", "description": "Promote peaceful and inclusive societies.", "link": "https://www.google.com/search?q=SDG+16+Peace+Justice+and+Strong+Institutions"},
        17: {"title": "Partnerships for the Goals", "description": "Strengthen implementation and revitalize global partnerships.", "link": "https://www.google.com/search?q=SDG+17+Partnerships+for+the+Goals"},
    }


    return render(request, "index.html", {"sdg_data": sdg_data})

@login_required
def dynamic_page(request, page_name):
    template_name = f"{page_name}.html"  # Construct template filename dynamically

    try:
        if template_name=="result-page.html":
             # Get values from profile or form
                profile = get_user_profile(request.user)
                # Get values from profile or form
                carbon_emissions = profile.carbon_score 
                energy_consumption = profile.energy_total 
                waste_production = profile.total_waste 
                eevta_score = profile.eevta_score
                content={"carbon_value": carbon_emissions,
                         "energy_value":energy_consumption,
                         "waste_value":waste_production,
                         "evtaa_value":eevta_score}
                return render(request,template_name,content)
            
        return render(request, template_name)  # Render the corresponding template
    except:
        return render(request, "index.html") 

# Calculator Views
@login_required
#carbon score calculation function.
def carbon_calculator(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                electricity_usage = float(request.POST.get('elec', '0') or 0)
                gas_consumption = float(request.POST.get('gas', '0') or 0)
                vehicle_fuel = float(request.POST.get('vefeul', '0') or 0)
                machinery_fuel = float(request.POST.get('machine', '0') or 0)
                short_flights = int(request.POST.get('flights-4-less', '0') or 0)
                long_flights = int(request.POST.get('flights-4-more', '0') or 0)
                transport_exp = float(request.POST.get('transexp', '0') or 0)
                inventory_exp = float(request.POST.get('invenexp', '0') or 0)
                services_exp = float(request.POST.get('servicesexp', '0') or 0)
                recycles_newspaper = request.POST.get('newspaperOptionsRadios', 'no') == 'yes'
                recycles_aluminum = request.POST.get('alumtinOptionsRadios', 'no') == 'yes'

                # Calculate score
                carbon_score = (electricity_usage * 0.5 + gas_consumption * 2.3 +
                              vehicle_fuel * 2.7 + machinery_fuel * 2.5 +
                              short_flights * 200 + long_flights * 500 +
                              transport_exp * 0.1 + inventory_exp * 0.1 + services_exp * 0.1)
                
                if recycles_newspaper:
                    carbon_score *= 0.9
                if recycles_aluminum:
                    carbon_score *= 0.9

                # Save to user profile
                profile = get_user_profile(request.user)
                profile.carbon_score = round(carbon_score, 2)
                profile.electricity_usage = electricity_usage
                profile.gas_consumption = gas_consumption
                profile.save()
                
                suggestions = [
                    "The average footprint for people in India is 1.73 metric tons.",
                    "The average for the European Union is about 6.4 metric tons.",
                    "The average worldwide carbon footprint is about 5 metric tons.",
                    "The worldwide target to combat climate change is 2 metric tons."]
                carbon_categories = {
                    "EXCELLENT": {"range": "438,000 or below", "color": "success"},
                    "GOOD": {"range": "438,000 to 1,167,927", "color": "info"},
                    "AVERAGE": {"range": "1,167,927 to 1,606,000", "color": "warning"},
                    "NEEDS WORK": {"range": "1,606,000 or above", "color": "danger"},
                    }
                return render(request, 'form_result.html', {
                    "heading":"Institutional Carbon Calculator",
                    "sub_heading":"Measure your organization's environmental impact and discover ways to improve your sustainability",
                    'score': round(carbon_score, 2),
                    'profile_id': profile.id,
                    "suggestions":suggestions,
                    "message":"This number represents the amount of greenhouse gases in units of carbon dioxide you emit per year",
                    'categories':carbon_categories,
                    'show_temp':True,
                    "page":"service-details"
                })

        except Exception as e:
            messages.error(request, f"Error calculating carbon footprint: {str(e)}")
            return render(request, 'service-details.html')
    
    return render(request, 'service-details.html')

@login_required
#Energy consumption calculation function.
def energy_calculator(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                electricity_kwh = float(request.POST.get('monthlyElectricity', 0) or 0)
                vehicle_fuel_liters = float(request.POST.get('vehicleFuel', 0) or 0)
                fuel_type = request.POST.get('fuelType')
                heating_fuel = float(request.POST.get('heatingFuel', 0) or 0)
                water_consumption = float(request.POST.get('waterConsumption', 0) or 0)

                # Calculate energy
                fuel_kwh = vehicle_fuel_liters * (9.1 if fuel_type == 'petrol' else 10.7 if fuel_type == 'diesel' else 9.5)
                heating_kwh = heating_fuel * 10
                water_kwh = water_consumption * 0.1
                total_consumption = electricity_kwh + fuel_kwh + heating_kwh + water_kwh

                # Save to user profile
                profile = get_user_profile(request.user)
                profile.energy_total = total_consumption
                profile.electricity_kwh = electricity_kwh
                profile.save()
                # Calculate industry averages
                industry_avg_energy = SustainabilityProfile.objects.aggregate(avg_energy=Avg('energy_total'))
                
                benchmark_data = {
                    "EXCELLENT": {"color": "success", "range": "Below industry average"},
                    "GOOD": {"color": "info", "range": "Near industry average"},
                    "AVERAGE": {"color": "warning", "range": "Industry standard"},
                    "NEEDS IMPROVEMENT": {"color": "danger", "range": "Above industry average"},
                }
                energy_saving_tips = [
                    "Upgrade to LED lighting throughout facilities",
                    "Implement smart thermostats for HVAC systems",
                    "Consider solar panel installation",
                    "Establish an employee energy awareness program",
                    "Conduct regular energy audits"
                ]
                consumption_breakdown = {
                        "Industry Average":{"id":"industry_avg","value":round(industry_avg_energy['avg_energy'],2),"unit":"units"},
                        "Electricity": {"id": "electricityBreakdown", "value": electricity_kwh, "unit": "kWh"},
                        "Vehicle Fuel": {"id": "fuelBreakdown", "value":  fuel_kwh, "unit": "liters"},
                        "Heating Fuel": {"id": "heatingBreakdown", "value": heating_kwh , "unit": "units"},
                        "Other Energy": {"id": "otherBreakdown", "value":  total_consumption, "unit": "units"},
                    }


                context = {
                    'score': round(total_consumption),
                    'profile_id': profile.id,
                    "heading":"Energy Consumption Calculator",
                    "sub_heading":"Measure your company's energy usage and identify opportunities for efficiency improvements",
                    "suggestions":energy_saving_tips ,
                    "message":"This represents you company's estimated monthly energy consumption",
                    "categories": benchmark_data,
                    "page":"service-details3",
                    "show_breakdown": True, 
                    "consumption_breakdown": consumption_breakdown
                }
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(context)
                
                return render(request, 'form_result.html', context)

        except Exception as e:
            messages.error(request, f"Error calculating energy consumption: {str(e)}")
            return render(request, 'service-details3.html')
    
    return render(request, 'service-details3.html')

#waste production calculation function.
@login_required
def waste_calculator(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                solid_waste = float(request.POST.get('swaste', 0) or 0)
                organic_waste = float(request.POST.get('owaste', 0) or 0)
                e_waste = float(request.POST.get('ewaste', 0) or 0)
                hazardous_waste = float(request.POST.get('Hwaste', 0) or 0)
                recycled_waste = float(request.POST.get('rcycwaste', 0) or 0)
                
                # Calculate waste metrics
                total_waste = solid_waste + organic_waste + e_waste + hazardous_waste
                reduction_rate = round((recycled_waste / total_waste) * 100) if total_waste > 0 else 0

                # Save to user profile
                profile = get_user_profile(request.user)
                profile.waste_reduction_rate = reduction_rate
                profile.total_waste = total_waste
                profile.recycled_waste = recycled_waste
                profile.save()
                
                waste_breakdown = {
                    "Solid Waste": {"id": "solidWaste", "value": "solid_waste", "unit": "kg"},
                    "Organic Waste": {"id": "organicWaste", "value": "organic_waste", "unit": "kg"},
                    "E-Waste": {"id": "eWaste", "value": "e_waste", "unit": "kg"},
                    "Hazardous Waste": {"id": "hazardousWaste", "value": "hazardous_waste", "unit": "kg"},
                    "Total Waste Generated": {"id": "totalWaste", "value": "total_waste", "unit": "kg"},
                    "Recycled Waste": {"id": "recycledWaste", "value": "recycled_waste", "unit": "kg"},
                }
                waste_reduction_tips = [
                    "Implement a comprehensive recycling program",
                    "Conduct waste audits every quarter",
                    "Educate staff about waste reduction",
                    "Partner with certified e-waste recyclers"
                ]
                benchmark_data= {
                    "EXCELLENT": {"range": "80-100%", "color": "success"},
                    "GOOD": {"range": "60-79%", "color": "info"},
                    "AVERAGE": {"range": "40-59%", "color": "warning"},
                    "NEEDS WORK": {"range": "Below 40%", "color": "danger"}
                }

                context = {
                    'score': reduction_rate,
                    'total_waste': total_waste,
                    'profile_id': profile.id,
                    "heading":"Waste Reduction Rate Calculator",
                    "sub_heading":"Measure your institution's waste reduction performance and sustainability progress",
                    "suggestions":waste_reduction_tips ,
                    "message":"Your waste reduction rate of your company based on the data provided",
                    "categories": benchmark_data,
                    "page":"service-details4",
                    "show_waste_breakdown": True,
                    "waste_breakdown": waste_breakdown
                }
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(context)
                
                return render(request, 'form_result.html', context)

        except Exception as e:
            messages.error(request, f"Error calculating waste metrics: {str(e)}")
            return render(request, 'ervice-details4.html')
    
    return render(request, 'ervice-details4.html')
 
#eevta (Electric & Efficient Vehicle Transition Aid) function
@login_required
def eevta_calculator(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data safely
                total_students = int(request.POST.get('totalStudents', '0') or 0)
                tech_voc_students = int(request.POST.get('techVocStudents', '0') or 0)
                distance_learning = int(request.POST.get('distanceLearning', '0') or 0)
                scholarship_students = int(request.POST.get('scholarshipStudents', '0') or 0)
                financial_aid = int(request.POST.get('financialAid', '0') or 0)
                grad_rate = min(int(request.POST.get('gradRate', '0') or 0), 100)
                employment_rate = min(int(request.POST.get('employmentRate', '0') or 0), 100)

                if total_students == 0:
                    return render(request, "service-details2.html", {"error": "Total students cannot be zero."})

                # Calculate percentages safely
                tech_voc_percentage = (tech_voc_students / total_students) * 100 if total_students != 0 else 0
                distance_learning_percentage = (distance_learning / total_students) * 100 if total_students != 0 else 0
                scholarship_percentage = (scholarship_students / total_students) * 100 if total_students != 0 else 0
                financial_aid_percentage = (financial_aid / total_students) * 100 if total_students != 0 else 0

                # Calculate score
                score = (min(tech_voc_percentage * 0.3, 10) +
                        min(distance_learning_percentage * 0.2, 20) +
                        min(scholarship_percentage * 0.3, 10) +
                        min(financial_aid_percentage * 0.2, 20) +
                        grad_rate * 0.2 +
                        employment_rate * 0.2)

                final_score = min(round(score), 100)

                # Save to user profile
                profile = get_user_profile(request.user)
                profile.eevta_score = final_score
                profile.total_students = total_students
                profile.tech_voc_percentage = tech_voc_percentage
                profile.save()
                
                benchmark_data = {
                "EXCELLENT": {"range": (85, 100), "color": "success"},
                "GOOD": {"range": (70, 84), "color": "info"},
                "AVERAGE": {"range": (50, 69), "color": "warning"},
                "NEEDS IMPROVEMENT": {"range": (0, 49), "color": "danger"},
                }

                key_recommendations = [
                    "Increase scholarship opportunities for underprivileged students",
                    "Expand distance learning programs for greater accessibility",
                    "Improve facilities for students with disabilities",
                    "Develop more flexible payment options",
                    "Enhance career counseling services",
                ]


                return render(request, 'form_result.html', {
                    'score': final_score,
                    'profile_id': profile.id,
                    "heading":"EEVTA Assessment Tool",
                    "sub_heading":"Measure your institution's performance in providing Equal Access to Affordable Technical, Vocational, and Higher Education",
                    "suggestions":key_recommendations,
                    "message":"This number represents you institute's EEVTA (Equal Access to Affordable Technical, Vocational, and Higher Education) score",
                    "categories": benchmark_data,
                    "page":"service-details2"
                })


        except ValueError:
            messages.error(request, "Invalid input. Please enter valid numbers.")
            return render(request, 'service-details2.html')
    
    return render(request, 'service-details2.html')

# Performance dashboard function
@login_required
def sustainability_dashboard(request):
    try:
        your_company = get_user_profile(request.user)
        # Get the next available row after your_company.id
        last_update = CalculationHistory.objects.filter(user=your_company.user).order_by('created_at').first()
            
        your_company_data = {
            "id_value":your_company.user,
            "company_name": your_company.company_name,
            "roi": your_company.roi,
            "sustainability_score": your_company.sustainability_score,
            "cost_benefit": your_company.cost_benefit,
            "carbon_score": your_company.carbon_score,
            "electricity_usage": your_company.electricity_usage,
            "waste_reduction_rate": your_company.waste_reduction_rate,
        }
    except SustainabilityProfile.DoesNotExist:
        your_company_data = None

    # Get all companies for ranking with username included
    ranked_companies_by_ss = list(SustainabilityProfile.objects.all()
                                .order_by('-sustainability_score')
                                .values('id', 'company_name', 'user__username', 'roi','sustainability_score', 'cost_benefit', 'carbon_score','industry','eevta_score'))

    ranked_companies_by_roi = list(SustainabilityProfile.objects.all()
                                .order_by('-roi')
                                .values('id', 'company_name', 'user__username', 'roi','sustainability_score', 'cost_benefit', 'carbon_score','industry','eevta_score'))

    ranked_companies_by_cost_benefits = list(SustainabilityProfile.objects.all()
                                            .order_by('-cost_benefit')
                                            .values('id', 'company_name', 'user__username', 'roi','sustainability_score', 'cost_benefit', 'carbon_score','industry','eevta_score'))

    # Get all companies ranked by composite score with username
    ranked_companies_by_composite = list(
        SustainabilityProfile.objects.annotate(
            composite_score=ExpressionWrapper(
                F('roi') * 0.4 + 
                F('sustainability_score') * 0.4 + 
                F('cost_benefit') * 0.2,
                output_field=FloatField()
            )
        ).order_by('-composite_score')
        .values('id', 'company_name', 'user__username', 'roi', 
                'sustainability_score', 'cost_benefit', 'carbon_score', 'composite_score','industry','eevta_score'))

    all_ranks = {
        "sustainability_score": ranked_companies_by_ss,
        "roi": ranked_companies_by_roi,
        "cost_benefit": ranked_companies_by_cost_benefits,
        "composite_score": ranked_companies_by_composite
    }

    my_rank = {}  # Store the ranking

    if your_company:
        for key, ranked_companies in all_ranks.items():
            for index, company in enumerate(ranked_companies, start=1):
                if company['id'] == your_company.id:
                    my_rank[key] = index
                    break

    # Calculate industry averages
    industry_stats = SustainabilityProfile.objects.aggregate(
        avg_roi=Avg('roi'),
        avg_sustainability=Avg('sustainability_score'),
        avg_carbon=Avg('carbon_score'),
        avg_energy=Avg('energy_total'),
        avg_waste=Avg('total_waste'),
        max_sustainability=Max('sustainability_score'),
        min_sustainability=Min('sustainability_score')
    )

    # Prepare trend data
    if your_company_data:

        # Radar chart data
        radar_labels = ['ROI', 'Sustainability', 'Cost-Benefit', 'Carbon Score', 'Energy Eff.', 'Waste Mgmt.']
        radar_your_data = [
            your_company.roi,
            your_company.sustainability_score,
            your_company.cost_benefit,
            100 - (your_company.carbon_score / 100 * 100),
            100 - (your_company.electricity_usage / 50000 * 100),
            your_company.waste_reduction_rate
        ]
        radar_industry_data = [
            industry_stats['avg_roi'],
            industry_stats['avg_sustainability'],
            industry_stats['avg_carbon'],
            100 - (industry_stats['avg_carbon'] / 100 * 100),
            100 - (industry_stats['avg_energy'] / 50000 * 100),
            50
        ]
    else:
        radar_labels = []
        radar_your_data = []
        radar_industry_data = []

    if last_update:
        roi_change=your_company.roi-last_update.roi
        sus_change=your_company.sustainability_score-last_update.sustainability_score
        cost_change=your_company.cost_benefit-last_update.cost_benefit
        energy_change = 0
        if last_update.energy_consumption and last_update.energy_consumption != 0:
          
            energy_change = ((your_company.energy_total - last_update.energy_consumption) / last_update.energy_consumption) * 100

        waste_change = 0
        if last_update.waste_production and last_update.waste_production != 0:
           
            waste_change = ((your_company.total_waste - last_update.waste_production) / last_update.waste_production) * 100
    
    else:
        energy_change = 0
        roi_change=0
        sus_change=0
        cost_change=0
        waste_change = 0
      
        
    last_update_date=last_update.updated_at if last_update else None  
    context = {
        'your_company':your_company_data,
        'industry_stats': industry_stats,
        'radar_labels': radar_labels,
        'radar_your_data': radar_your_data,
        'radar_industry_data': radar_industry_data,
        'sorted_data':all_ranks,
        'my_rank':my_rank,
        "roi_change":round(roi_change,1),
        "sus_change":round(sus_change,1),
        "cost_change":round(cost_change,1),
        "energy_change":round(energy_change,2),
        "waste_change":round(waste_change,2),
    }
    
    return render(request, 'dashboard.html', {"context_data": json.dumps({
    "context": context
}, default=str), **context,"last_update":last_update_date})
   
    
#sustainability score function.
@login_required
def calculate_sustainability_score(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                profile = get_user_profile(request.user)

                # Get values from profile or form
                industry=request.POST.get("industry") if request.POST.get("industry") else profile.industry if profile else "N/A"
                carbon_emissions = float(request.POST.get('carbon')) if request.POST.get('carbon') else (profile.carbon_score if profile else 0)
                energy_consumption = float(request.POST.get('energy')) if request.POST.get('energy') else (profile.energy_total if profile else 0)
                waste_production = float(request.POST.get('waste')) if request.POST.get('waste') else (profile.total_waste if profile else 0)
                eevta_score = float(request.POST.get('evtaa')) if request.POST.get('evtaa') else (profile.eevta_score if profile else 0)
        
                # Get financial data
                revenue = float(request.POST.get('revenue', 0)or 0)
                costs = float(request.POST.get('cost', 0) or 0)
                investment = float(request.POST.get('inv', 0)or 0)
                
                # Calculate metrics
                sustainability_score = min(
                    (max(0, 100 - carbon_emissions/10) * 0.3 + 
                     max(0, 100 - energy_consumption/1000) * 0.2 + 
                     max(0, 100 - waste_production/100) * 0.2 + 
                     eevta_score * 0.3), 
                    100
                )
                
                profit = revenue - costs
                roi = (profit / investment) * 100 if investment > 0 else 0
                benefit = profit + (sustainability_score * 1000)
                cost_benefit = benefit / investment if investment > 0 else 0
                
                # Save final results
                profile.industry=industry
                profile.carbon_score=carbon_emissions  
                profile.energy_total=energy_consumption 
                profile.total_waste = waste_production 
                profile.eevta_score =eevta_score 
                profile.sustainability_score = sustainability_score
                profile.roi = roi
                profile.cost_benefit = cost_benefit
                profile.save()

                context = {
                    'heading':"Transforming Sustainability",
                    "sub_heading":"Sustainable process for better future.",
                    'sustainability_score': round(sustainability_score),
                    'roi': round(roi),
                    'cost_benefit': round(cost_benefit, 1),
                    'profile_id': profile.id,
                }
                save_profile_to_history(request.user)
                return render(request, 'agg_res.html', context)

        except Exception as e:
            messages.error(request, f"Error calculating sustainability score: {str(e)}")
            return render(request, 'result-page.html')
    
    return render(request, 'result-page.html')


#save user history.   
def save_profile_to_history(user):
    """Save the current SustainabilityProfile data to CalculationHistory."""
    
    profile = SustainabilityProfile.objects.get(user=user)

    # Create a new entry in CalculationHistory using profile data
    history = CalculationHistory.objects.create(
        user=user,
        profile=profile,
        
        # Copying relevant values from SustainabilityProfile to history
        carbon_emissions=profile.carbon_score,
        energy_consumption=profile.energy_total,
        waste_production=profile.total_waste,
        eevta_score=profile.eevta_score,
        revenue=0,  # Update if applicable
        costs=0,    # Update if applicable
        investment=0,  # Update if applicable
        sustainability_score=profile.sustainability_score,
        roi=profile.roi,
        cost_benefit=profile.cost_benefit,
        created_at=datetime.now()
    )
    # Keep only the latest 5 entries, delete older ones
    user_histories = CalculationHistory.objects.filter(user=user).order_by('-created_at')
    if user_histories.count() > 20:
        old_ids = user_histories.values_list('id', flat=True)[20:]  # Get IDs of older records
        CalculationHistory.objects.filter(id__in=old_ids).delete()  # Delete all entries except the latest 5

    return history  


@login_required
def calculation_history(request):
    """
    Retrieve and display the user's calculation history in a table
    """
    histories = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')

    first_entry = histories.first()  # First record (most recent)
    last_entry = histories.last()  # Last record (oldest)

    return render(request, 'history.html', {
        'histories': histories,
        'first_entry': first_entry,
        'last_entry': last_entry,
    })
import pandas as pd    
def import_sustainability_profiles(csv_file_path):
  df = pd.read_csv(csv_file_path)

  for index, row in df.iterrows():
      # Fetch or create a user using company name (modify if needed)
      user, created = User.objects.get_or_create(username=row["company_name"])

      # Create or update the sustainability profile
      profile, _ = SustainabilityProfile.objects.update_or_create(
          user=user,
          defaults={
              "company_name": row["company_name"],
              "carbon_score": row["carbon_score"],
              "industry":row["industry"],
              "electricity_usage": row["electricity_usage"],
              "total_waste": row["total_waste"],
              "eevta_score": row["eevta_score"],
              "sustainability_score": row["sustainability_score"],
              "roi": row["roi"],
              "cost_benefit": row["cost_benefit"],
          }
      )

  print("Sustainability profiles imported successfully!")
import_sustainability_profiles("./static/cleaned_company_data.csv")
