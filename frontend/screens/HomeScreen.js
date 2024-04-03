import { StyleSheet, Text, TextInput, View, Button } from 'react-native';
import React, {useState} from 'react';
import Dashboard from './Dashboard.js'

function HomeScreen( {navigation}){
    const [leagueID,setLeagueID] = useState('')
    return (
        <View>
            <Text>Fantasy Optimizer</Text>
            <TextInput
            placeholder = 'League ID:'
            onChangeText = {newText => setLeagueID(newText)}
            defaultValue = {leagueID}
            />

            <Button
                title = "GOGO"
                onPress = { () => navigation.navigate('Dashboard', {leagueID: {leagueID}})}
            />
        </View>
    )
}
export default HomeScreen
