#!/usr/bin/env python3
"""
Monitoring script for the PolyRatings scraper.
Checks data freshness, completeness, and provides health metrics.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

def load_data() -> Optional[Dict]:
    """Load the scraped data file."""
    data_file = Path("data/professors.json")
    if not data_file.exists():
        print("❌ No data file found at data/professors.json")
        return None
    
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error reading data file: {e}")
        return None

def check_data_freshness(data: Dict) -> bool:
    """Check if the data is fresh (less than 24 hours old)."""
    if 'scraped_at' not in data:
        print("❌ No timestamp found in data")
        return False
    
    try:
        scraped_at = datetime.fromisoformat(data['scraped_at'].replace('Z', '+00:00'))
        now = datetime.utcnow().replace(tzinfo=scraped_at.tzinfo)
        age = now - scraped_at
        
        print(f"📅 Data age: {age}")
        
        if age > timedelta(hours=24):
            print("⚠️  Data is more than 24 hours old")
            return False
        else:
            print("✅ Data is fresh")
            return True
    except Exception as e:
        print(f"❌ Error parsing timestamp: {e}")
        return False

def check_data_completeness(data: Dict) -> Dict:
    """Check the completeness of the scraped data."""
    stats = {
        'total_professors': data.get('total_professors', 0),
        'professors_with_ratings': 0,
        'professors_with_reviews': 0,
        'professors_with_departments': 0,
        'departments_count': 0,
        'avg_rating': 0.0,
        'rating_distribution': {}
    }
    
    professors = data.get('professors', [])
    departments = set()
    total_rating = 0.0
    rating_count = 0
    
    for prof in professors:
        # Count professors with ratings
        if prof.get('rating') is not None:
            stats['professors_with_ratings'] += 1
            total_rating += prof['rating']
            rating_count += 1
            
            # Track rating distribution
            rating_floor = int(prof['rating'])
            stats['rating_distribution'][rating_floor] = stats['rating_distribution'].get(rating_floor, 0) + 1
        
        # Count professors with review counts
        if prof.get('review_count') is not None and prof['review_count'] > 0:
            stats['professors_with_reviews'] += 1
        
        # Count professors with departments
        if prof.get('department') and prof['department'].strip():
            stats['professors_with_departments'] += 1
            departments.add(prof['department'])
    
    stats['departments_count'] = len(departments)
    stats['avg_rating'] = total_rating / rating_count if rating_count > 0 else 0.0
    
    return stats

def print_health_report(data: Dict, stats: Dict):
    """Print a comprehensive health report."""
    print("\n" + "="*50)
    print("🏥 POLYRATINGS SCRAPER HEALTH REPORT")
    print("="*50)
    
    # Basic info
    print(f"📊 Total Professors: {stats['total_professors']}")
    print(f"📅 Last Scraped: {data.get('scraped_at', 'Unknown')}")
    
    # Completeness metrics
    print(f"\n📈 Completeness Metrics:")
    print(f"   • Professors with ratings: {stats['professors_with_ratings']} ({stats['professors_with_ratings']/stats['total_professors']*100:.1f}%)")
    print(f"   • Professors with reviews: {stats['professors_with_reviews']} ({stats['professors_with_reviews']/stats['total_professors']*100:.1f}%)")
    print(f"   • Professors with departments: {stats['professors_with_departments']} ({stats['professors_with_departments']/stats['total_professors']*100:.1f}%)")
    print(f"   • Unique departments: {stats['departments_count']}")
    
    # Rating statistics
    print(f"\n⭐ Rating Statistics:")
    print(f"   • Average rating: {stats['avg_rating']:.2f}")
    print(f"   • Rating distribution:")
    for rating in sorted(stats['rating_distribution'].keys()):
        count = stats['rating_distribution'][rating]
        percentage = count / stats['professors_with_ratings'] * 100
        bars = "█" * int(percentage / 5)  # Visual bar
        print(f"     {rating}⭐: {count:4d} ({percentage:5.1f}%) {bars}")
    
    # Health assessment
    print(f"\n🔍 Health Assessment:")
    if stats['total_professors'] < 1000:
        print("   ⚠️  Low professor count - scraper may not be working properly")
    elif stats['total_professors'] < 2000:
        print("   ⚠️  Moderate professor count - some data may be missing")
    else:
        print("   ✅ Good professor count")
    
    if stats['professors_with_ratings'] / stats['total_professors'] < 0.8:
        print("   ⚠️  Many professors missing ratings")
    else:
        print("   ✅ Good rating coverage")
    
    if stats['professors_with_departments'] / stats['total_professors'] < 0.8:
        print("   ⚠️  Many professors missing department info")
    else:
        print("   ✅ Good department coverage")

def main():
    """Main monitoring function."""
    print("🔍 PolyRatings Scraper Monitor")
    print("="*40)
    
    # Load data
    data = load_data()
    if not data:
        return 1
    
    # Check freshness
    is_fresh = check_data_freshness(data)
    
    # Check completeness
    stats = check_data_completeness(data)
    
    # Print health report
    print_health_report(data, stats)
    
    # Overall status
    print(f"\n🎯 Overall Status:")
    if is_fresh and stats['total_professors'] >= 2000:
        print("   ✅ HEALTHY - Data is fresh and complete")
        return 0
    elif is_fresh:
        print("   ⚠️  WARNING - Data is fresh but may be incomplete")
        return 1
    else:
        print("   ❌ CRITICAL - Data is stale or incomplete")
        return 2

if __name__ == "__main__":
    exit(main()) 
