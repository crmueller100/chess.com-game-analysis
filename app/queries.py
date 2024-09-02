import pymongo
from pprint import pprint
from datetime import datetime
import chess.pgn 

from connect_to_mongo import connect_to_mongo

def get_latest_game(collection, player):
    filter_query = { "player": player }
    return collection.find_one(filter_query, sort=[("end_time", pymongo.DESCENDING)], projection={"end_time": 1})

def get_all_games(collection, player, time_class=None, color=None, date=None):
    filter_query = { "player": player }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}
    if date:
        filter_query["end_time"] = {"$gte": date}

    return collection.count_documents(filter_query)

def get_all_games_as_white(collection, player, time_class=None, color=None, date=None):
    filter_query = {
        # makes it a case-insensitive search
        "white.username": {"$regex": f"^{player}$", "$options": "i"},
        "player": player
    }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}
    if date:
        filter_query["end_time"] = {"$gte": date}

    return collection.count_documents(filter_query)

def get_all_games_as_black(collection, player, time_class=None, color=None, date=None):
    filter_query = {
        # makes it a case-insensitive search
        "black.username": {"$regex": f"^{player}$", "$options": "i"},
        "player": player
    }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}
    if date:
        filter_query["end_time"] = {"$gte": date}

    return collection.count_documents(filter_query)

def get_all_games_played_in_a_month(collection, player, month, time_class=None, color=None, date=None):
    filter_query = {
        "player": player,
        "month": month
    }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}
    if date:
        filter_query["end_time"] = {"$gte": date}

    return collection.count_documents(filter_query)


def get_win_loss_counts(collection, player, color, time_class=None, color_filter=None, date=None):

    pipeline = [
        {
            "$match": {
                f"{color}.username": {"$regex": player, "$options": "i"},
                **({"time_class": time_class} if time_class else {}),
                **({f"{color_filter}.username": {"$regex": f"^{player}$", "$options": "i"}} if color_filter else {}),
                **({"end_time": {"$gte": date}} if date else {})
                
            }
        },
        {
            # This creates a new field called "result" that contains the value of "{color}.result"
            "$project": { 
                "result": f"${color}.result"
            }
        },
        {
            "$group": {
                "_id": "$result",
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result

def count_time_controls(collection, player, time_class=None, color=None, date=None):
    pipeline = [
        {
            "$match": {
                f"player": {"$regex": player, "$options": "i"},
                **({"time_class": time_class} if time_class else {}),
                **({f"{color}.username": {"$regex": f"^{player}$", "$options": "i"}} if color else {}),
                **({"end_time": {"$gte": date}} if date else {}),
            }
        },
        {
            "$project": { 
                "result": "$time_class"
            }
        },
        {
            "$group": {
                "_id": "$result",
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result

def count_detailed_time_controls(collection, player, time_class=None, color=None, date=None):
    pipeline = [
        {
            "$match": {
                "player": {"$regex": player, "$options": "i"},
                **({"time_class": time_class} if time_class else {}),  # Filter by time_class (if provided)
                **({f"{color}.username": {"$regex": f"^{player}$", "$options": "i"}} if color else {}),  # Filter by color (if provided)
                **({"end_time": {"$gte": date}} if date else {}),
            }
        },
        {
            "$project": {
                "result": {
                    "$cond": {
                        "if": { "$eq": ["$time_class", "daily"] },
                        "then": "daily",
                        "else": {
                            "$cond": {
                                "if": { "$eq": ["$time_class", "blitz"] },
                                "then": {
                                    "$switch": {
                                        "branches": [
                                            { "case": { "$and": [{"$eq": ["$time_class", "blitz"]}, {"$eq": ["$time_control", "300"] }] }, "then": "5 minute blitz" },
                                            { "case": { "$and": [{"$eq": ["$time_class", "blitz"]}, {"$eq": ["$time_control", "180"] }] }, "then": "3 minute blitz" }
                                        ],
                                        "default": "blitz"
                                    }
                                },
                                "else": {
                                    "$cond": {
                                        "if": { "$eq": ["$time_class", "bullet"] },
                                        "then": {
                                            "$switch": {
                                                "branches": [
                                                    { "case": { "$and": [{"$eq": ["$time_class", "bullet"]}, {"$eq": ["$time_control", "60"] }] }, "then": "1 minute bullet" },
                                                    { "case": { "$and": [{"$eq": ["$time_class", "bullet"]}, {"$eq": ["$time_control", "30"] }] }, "then": "30 second bullet" }
                                                ],
                                                "default": "bullet"
                                            }
                                        },
                                        "else": "$time_class"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$result",
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result

def rating_of_time_controls_over_time(collection, player, time_class, color, date=None):
    # Try new way of organizing the stages

    stage_match_filters = {
        "$match": {
            "player": {"$regex": player, "$options": "i"},
            **({"time_class": time_class} if time_class else {}),  # Filter by time_class (if provided)
            **({f"{color}.username": {"$regex": f"^{player}$", "$options": "i"}} if color else {}),  # Filter by color (if provided)
            **({"end_time": {"$gte": date}} if date else {}),
        }
    }

    project_day_and_time_class = {
        "$project": {
            "result": "$time_class",
            "date": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": {
                        "$toDate": {
                            "$multiply": ["$end_time", 1000] # Convert to milliseconds
                        }
                    }
                }
            },
            # need to determine the player's color to determine their rating
            "player_color": {
                "$cond": [
                    {"$eq": [{"$toLower": "$white.username"}, {"$toLower": player}]},
                    "white",
                    "black"
                ]
            },
            "rating": {
                "$cond": [
                    # Need to re-evaluate the player color because these expressions are evaluated independently for each document
                    {"$eq": [{
                        "$cond": [{
                            "$eq": [{"$toLower": "$white.username"}, {"$toLower": player}]
                            },
                        "white",
                        "black"
                        ]
                    }, 
                    "white"]},
                    "$white.rating",
                    "$black.rating"
                ]
            }
        }
    }
    group_by_day_and_time_class = {
        "$group": {
            "_id": {
                "time_class": "$result",
                "date": "$date"
            },
            "avg_rating": {"$avg": "$rating"}, #Calculate average of the player's rating
            "count": {"$sum": 1}
        }
    }

    project = {
        "$project": {
            "_id": 0,
            "time_class": "$_id.time_class",
            "date": "$_id.date",
            "avg_rating": 1,
            "count": 1
        }
    }

    sort = {
        "$sort": {
            "date": pymongo.ASCENDING
        }
    }

    pipeline = [
        stage_match_filters,
        project_day_and_time_class,
        group_by_day_and_time_class,
        project,
        sort
    ]

    result = list(collection.aggregate(pipeline))
    return result

def summary_of_all_eco_openings(collection, player, time_class=None, color=None, date=None, eco_opening="eco_opening"):
    pipeline = [
        {
            "$match": {
                f"player": {"$regex": player, "$options": "i"},
                **({"time_class": time_class} if time_class else {}),
                **({f"{color}.username": {"$regex": f"^{player}$", "$options": "i"}} if color else {}),
                **({"end_time": {"$gte": date}} if date else {}),
            }
        },
        {
            "$group": {
                "_id": f"${eco_opening}",
                "total_games": {"$sum": 1},
                "won": {
                    "$sum": {
                        "$cond": [
                            {"$or": [
                                {"$and": [{"$eq": [{"$toLower": "$white.username"}, player]}, {"$in": ["$white.result", ["win"]]}]},
                                {"$and": [{"$eq": [{"$toLower": "$black.username"}, player]}, {"$in": ["$black.result", ["win"]]}]}
                            ]},
                            1,
                            0
                        ]
                    }
                },
                "draw": {
                    "$sum": {
                        "$cond": [
                            {"$or": [
                                {"$and": [{"$eq": [{"$toLower": "$white.username"}, player]}, {"$in": ["$white.result", ["50move","agreed","insufficient","repetition","stalemate","timevsinsufficient"]]}]},
                                {"$and": [{"$eq": [{"$toLower": "$black.username"}, player]}, {"$in": ["$black.result", ["50move","agreed","insufficient","repetition","stalemate","timevsinsufficient"]]}]}
                            ]},
                            1,
                            0
                        ]
                    }
                },
                "lost": {
                    "$sum": {
                        "$cond": [
                            {"$or": [
                                {"$and": [{"$eq": [{"$toLower": "$white.username"}, player]}, {"$in": ["$white.result", ["resigned","checkmated","timeout","abandoned"]]}]},
                                {"$and": [{"$eq": [{"$toLower": "$black.username"}, player]}, {"$in": ["$black.result", ["resigned","checkmated","timeout","abandoned"]]}]}
                            ]},
                            1,
                            0
                        ]
                    }
                }
            }
        },
        {
            "$addFields": {
                "percent_won": {"$cond": [{"$gt": ["$total_games", 0]}, {"$multiply": [{"$divide": ["$won", "$total_games"]}, 100]}, 0]},
                "percent_draw": {"$cond": [{"$gt": ["$total_games", 0]}, {"$multiply": [{"$divide": ["$draw", "$total_games"]}, 100]}, 0]},
                "percent_lost": {"$cond": [{"$gt": ["$total_games", 0]}, {"$multiply": [{"$divide": ["$lost", "$total_games"]}, 100]}, 0]}
            }
        },
        {
            "$sort": {"total_games": pymongo.DESCENDING}  # Sort by total games in descending order
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result

def opening_move_win_loss_ratio(collection, player, time_class=None, color=None, date=None):
    filter_query = { "player": player }
    if time_class:
        filter_query["time_class"] = time_class
    if color:
        filter_query[f"{color}.username"] = {"$regex": f"^{player}$", "$options": "i"}
    if date:
        filter_query["end_time"] = {"$gte": date}

    return collection.find(filter_query)
    

#######################################################
# Queries for Stockfish Analysis
#######################################################

def build_filter_query(collection, player=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = {}

    # Combine $or conditions for each player individually (if provided)
    player1_filters = []
    if player:
        player1_filters.extend([
            {"white.username": {"$regex": f"^{player}$", "$options": "i"}}, 
            {"black.username": {"$regex": f"^{player}$", "$options": "i"}}
        ])

    player2_filters = []
    if player2:
        player2_filters.extend([
            {"white.username": {"$regex": f"^{player2}$", "$options": "i"}},
            {"black.username": {"$regex": f"^{player2}$", "$options": "i"}}
        ])

    # Combine player filters using $and if both players are provided
    if player and player2:
        filter_query["$and"] = [
            {"$or": player1_filters},
            {"$or": player2_filters}
        ]
    elif player:
        filter_query["$or"] = player1_filters
    elif player2:
        filter_query["$or"] = player2_filters

    if time_class:
        filter_query["time_class"] = time_class

    if date_start and not date_end:
        filter_query["end_time"] = {"$gte": date_start}

    if not date_start and date_end:
        filter_query["end_time"] = {"$lte": date_end}

    if date_start and date_end:
        filter_query["end_time"] = {"$gte": date_start, "$lte": date_end}

    return filter_query


def display_100_games(collection, player1=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = build_filter_query(collection, player1, player2, time_class, date_start, date_end)
    
    return collection.find(filter_query).limit(100)

def count_number_of_games_analyzed(collection, player1=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = build_filter_query(collection, player1, player2, time_class, date_start, date_end)
    filter_query["player_expectation"] = {"$exists": True}

    count = collection.count_documents(filter_query)
    return count

def count_number_of_games_analyzed(collection, player1=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = build_filter_query(collection, player1, player2, time_class, date_start, date_end)
    filter_query["player_expectation"] = {"$exists": True}

    count = collection.count_documents(filter_query)
    return count

def count_number_of_blunders(collection, player1=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = build_filter_query(collection, player1, player2, time_class, date_start, date_end)

    pipeline = [
        {"$match": filter_query},
        {"$group": {"_id": None, "total_blunders": {"$sum": {"$ifNull": ["$num_blunders", 0]}}}}
    ]

    result = list(collection.aggregate(pipeline))
    if result:
        total_blunders = result[0]["total_blunders"]
        return total_blunders 
    else:
        return 0

def count_number_of_inaccuracies(collection, player1=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = build_filter_query(collection, player1, player2, time_class, date_start, date_end)

    pipeline = [
        {"$match": filter_query},
        {"$group": {"_id": None, "total_inaccuracies": {"$sum": {"$ifNull": ["$num_inaccuracies", 0]}}}}
    ]

    result = list(collection.aggregate(pipeline))
    if result:
        total_blunders = result[0]["total_inaccuracies"]
        return total_blunders 
    else:
        return 0

def count_number_of_mistakes(collection, player1=None, player2=None, time_class=None, date_start=None, date_end=None):
    filter_query = build_filter_query(collection, player1, player2, time_class, date_start, date_end)

    pipeline = [
        {"$match": filter_query},
        {"$group": {"_id": None, "total_mistakes": {"$sum": {"$ifNull": ["$num_mistakes", 0]}}}}
    ]

    result = list(collection.aggregate(pipeline))
    if result:
        total_blunders = result[0]["total_mistakes"]
        return total_blunders 
    else:
        return 0

